
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task, Activity
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from .serializers import TaskSerializer
from django.contrib.auth.models import User



def dashboard(request):
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status="done").count()
    active_tasks = Task.objects.filter(status="in_progress").count()
    total_projects = Project.objects.count()

    recent_tasks = Task.objects.select_related("project").order_by(
        "-id"
    )[:5]

    recent_activities = Activity.objects.order_by(
        "-created_at"
    )[:5]

    context = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "active_tasks": active_tasks,
        "total_projects": total_projects,
        "recent_tasks": recent_tasks,
        "recent_activities": recent_activities,
    }

    return render(request, "dashboard/dashboard.html", context)


def projects(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if name:
            Project.objects.create(
                name=name,
                description=description
            )
            return redirect("projects")

    projects_list = Project.objects.all().order_by("-id")

    return render(
        request,
        "dashboard/projects.html",
        {"projects": projects_list}
    )

def tasks(request):
    projects_list = Project.objects.all().order_by("name")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        project_id = request.POST.get("project")
        status = request.POST.get("status", "new")
        priority = request.POST.get("priority", "medium")
        deadline = request.POST.get("deadline") or None

        if title and project_id:
            Task.objects.create(
                title=title,
                description=description,
                project_id=project_id,
                status=status,
                priority=priority,
                deadline=deadline,
            )
            return redirect("tasks")

    tasks_list = Task.objects.select_related("project").order_by("-id")

    context = {
        "projects": projects_list,
        "tasks": tasks_list,
        "users": User.objects.all().order_by("username"),
    }

    return render(request, "dashboard/tasks.html", context)


@require_POST
def create_task_ajax(request):
    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    project_id = request.POST.get("project")
    status = request.POST.get("status", "new")
    priority = request.POST.get("priority", "medium")
    deadline = request.POST.get("deadline") or None

    if not title or not project_id:
        return JsonResponse(
            {"success": False, "error": "Укажи название и проект"},
            status=400
        )

    if status not in dict(Task.STATUS_CHOICES):
        return JsonResponse(
            {"success": False, "error": "Некорректный статус"},
            status=400
        )

    if priority not in dict(Task.PRIORITY_CHOICES):
        return JsonResponse(
            {"success": False, "error": "Некорректный приоритет"},
            status=400
        )

    if deadline:
        from datetime import date

        try:
            date.fromisoformat(deadline)
        except ValueError:
            return JsonResponse(
                {"success": False, "error": "Некорректная дата"},
                status=400
            )

    if not Project.objects.filter(id=project_id).exists():
        return JsonResponse(
            {"success": False, "error": "Проект не найден"},
            status=400
        )

    with transaction.atomic():
        task = Task.objects.create(
            title=title,
            description=description,
            project_id=project_id,
            status=status,
            priority=priority,
            deadline=deadline,
            owner=request.user if request.user.is_authenticated else None,
        )

        Activity.objects.create(
            task=task,
            event_type="created",
            description=f"Создана задача «{task.title}».",
            actor=request.user if request.user.is_authenticated else None,
        )

    return JsonResponse({
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "project": task.project.name,
            "status": task.get_status_display(),
            "priority": task.get_priority_display(),
            "deadline": (
                task.deadline.strftime("%d.%m.%Y")
                if task.deadline and hasattr(task.deadline, "strftime")
                else "Не указан"
            ),
            "description": task.description,
        }
    })
@require_POST
def update_task_status(request, task_id):
    from django.shortcuts import get_object_or_404

    task = get_object_or_404(Task, id=task_id)
    status = request.POST.get("status")

    if status not in dict(Task.STATUS_CHOICES):
        return JsonResponse(
            {"success": False, "error": "Некорректный статус"},
            status=400
        )

    task.status = status
    task.save(update_fields=["status"])

    Activity.objects.create(
        task=task,
        description=f'Статус задачи «{task.title}» изменён на «{task.get_status_display()}»'
    )

    return JsonResponse({
        "success": True,
        "status": task.get_status_display()
    })
@require_POST
def delete_task_ajax(request, task_id):
    from django.shortcuts import get_object_or_404

    task = get_object_or_404(Task, id=task_id)
    title = task.title

    Activity.objects.create(
        task=None,
        description=f'Задача «{title}» удалена'
    )

    task.delete()

    return JsonResponse({
        "success": True,
        "message": "Задача удалена"
    })

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .serializers import ProjectSerializer, TaskSerializer, ActivitySerializer


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.all()

        status_filter = self.request.query_params.get("status")
        priority_filter = self.request.query_params.get("priority")

        if status_filter:
            if status_filter not in dict(Task.STATUS_CHOICES):
                return queryset.none()
            queryset = queryset.filter(status=status_filter)

        if priority_filter:
            if priority_filter not in dict(Task.PRIORITY_CHOICES):
                return queryset.none()
            queryset = queryset.filter(priority=priority_filter)

        return queryset


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get("status")
        reason = request.data.get("reason", "").strip()
        assignee_id = request.data.get("assignee")

        transitions = {
            "new": ["pending"],
            "pending": ["assigned", "rejected"],
            "assigned": ["in_progress"],
            "in_progress": ["done"],
        }

        if new_status not in transitions.get(task.status, []):
            raise ValidationError(
                {"status": "Недопустимый переход статуса."}
            )

        event_type = {
            "pending": "submitted",
            "in_progress": "started",
            "done": "completed",
        }.get(new_status, new_status)
        description = ""

        if new_status == "pending":
            description = "Задача отправлена на согласование."

        elif new_status == "assigned":
            if not assignee_id:
                raise ValidationError(
                    {"assignee": "Укажите исполнителя."}
                )

            from django.contrib.auth.models import User

            try:
                assignee = User.objects.get(pk=assignee_id)
            except User.DoesNotExist:
                raise ValidationError(
                    {"assignee": "Пользователь не найден."}
                )

            description = f"Назначен исполнитель: {assignee.username}."

        elif new_status == "rejected":
            if not reason:
                raise ValidationError(
                    {"reason": "Укажите причину отклонения."}
                )

            task.rejection_reason = reason
            description = f"Задача отклонена: {reason}"

        elif new_status == "in_progress":
            if task.assignee_id != request.user.id:
                raise PermissionDenied(
                    "Начать выполнение может только назначенный исполнитель."
                )

            description = "Исполнитель начал работу."

        elif new_status == "done":
            if task.assignee_id != request.user.id:
                raise PermissionDenied(
                    "Завершить задачу может только назначенный исполнитель."
                )

            description = "Задача завершена."

        with transaction.atomic():
            task.status = new_status

            if new_status == "assigned":
                task.assignee = assignee

            task.save()

            Activity.objects.create(
                task=task,
                event_type=event_type,
                description=description,
                actor=request.user,
            )

        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_200_OK
        )

    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user
        ).select_related("project", "owner", "assignee")

    def perform_create(self, serializer):
        with transaction.atomic():
            task = serializer.save(owner=self.request.user)

            Activity.objects.create(
                task=task,
                event_type="created",
                description=f"Создана задача «{task.title}».",
                actor=self.request.user
            )

    def perform_update(self, serializer):
        task = self.get_object()

        if task.owner != self.request.user:
            raise PermissionDenied(
                "Вы не можете изменять чужую задачу."
            )

        serializer.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            Activity.objects.create(
                task=None,
                event_type="deleted",
                description=f"Удалена задача «{instance.title}» (ID: {instance.id}).",
                actor=self.request.user,
            )
            instance.delete()


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from django.db.models import Q

        return Activity.objects.filter(
            Q(task__owner=self.request.user) |
            Q(task__isnull=True, actor=self.request.user)
        ).select_related("task", "actor").order_by("-created_at")


import os

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect


@staff_member_required
@require_POST
@csrf_protect
def import_dashboard_data_view(request):
    if os.environ.get("IMPORT_DASHBOARD_DATA") != "true":
        return HttpResponseForbidden("Импорт отключён.")

    if not request.user.is_superuser:
        return HttpResponseForbidden("Требуются права суперпользователя.")

    from .import_data import import_dashboard_data

    try:
        result = import_dashboard_data("dashboard_data.json")
    except Exception as exc:
        return HttpResponse(
            f"Импорт отменён: {exc}",
            status=400,
            content_type="text/plain; charset=utf-8",
        )

    return HttpResponse(
        "Импорт завершён: "
        f"{result['projects']} проектов, "
        f"{result['tasks']} задач, "
        f"{result['activities']} записей истории."
    )
