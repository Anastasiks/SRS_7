
import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Project, Task, Activity


def import_dashboard_data(file_path):
    file_path = Path(file_path)

    with file_path.open("r", encoding="cp1251") as file:
        records = json.load(file)

    User = get_user_model()
    admin = User.objects.filter(username="studyflow_admin").first()

    if admin is None:
        raise RuntimeError("Пользователь studyflow_admin не найден.")

    with transaction.atomic():
        if Project.objects.exists() or Task.objects.exists() or Activity.objects.exists():
            raise RuntimeError(
                "В базе уже есть данные dashboard. Импорт отменён."
            )

        project_map = {}
        task_map = {}

        for record in records:
            if record["model"] != "dashboard.project":
                continue

            fields = record["fields"]
            project = Project(
                name=fields["name"],
                description=fields.get("description", ""),
            )
            Project.objects.filter(pk=project.pk).exists()
            project.save()
            Project.objects.filter(pk=project.pk).update(
                created_at=fields["created_at"]
            )
            project_map[record["pk"]] = project

        for record in records:
            if record["model"] != "dashboard.task":
                continue

            fields = record["fields"]
            project = project_map.get(fields["project"])

            if project is None:
                raise RuntimeError(
                    f"Не найден проект для задачи {record['pk']}."
                )

            task = Task.objects.create(
                title=fields["title"],
                description=fields.get("description", ""),
                project=project,
                owner=admin if fields.get("owner") is not None else None,
                assignee=admin if fields.get("assignee") is not None else None,
                status=fields.get("status", "new"),
                priority=fields.get("priority", "medium"),
                deadline=fields.get("deadline"),
                rejection_reason=fields.get("rejection_reason", ""),
            )
            Task.objects.filter(pk=task.pk).update(
                created_at=fields["created_at"]
            )
            task_map[record["pk"]] = task

        for record in records:
            if record["model"] != "dashboard.activity":
                continue

            fields = record["fields"]
            old_task_id = fields.get("task")

            activity = Activity.objects.create(
                task=task_map.get(old_task_id),
                event_type=fields.get("event_type", "updated"),
                description=fields["description"],
                actor=admin if fields.get("actor") is not None else None,
            )
            Activity.objects.filter(pk=activity.pk).update(
                created_at=fields["created_at"]
            )

    return {
        "projects": Project.objects.count(),
        "tasks": Task.objects.count(),
        "activities": Activity.objects.count(),
    }
