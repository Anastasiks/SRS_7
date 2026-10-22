
from django.urls import path
from django.urls import include
from . import views
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, ProjectViewSet, ActivityViewSet
router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="api-tasks")
router.register(r"projects", ProjectViewSet, basename="api-projects")
router.register(r"history", ActivityViewSet, basename="api-history")

urlpatterns = [

    path("", views.dashboard, name="dashboard"),
    path("projects/", views.projects, name="projects"),
    path("tasks/", views.tasks, name="tasks"),

    # AJAX-обработчики должны идти перед REST API
    path("api/tasks/create/", views.create_task_ajax, name="create_task_ajax"),
    path(
        "api/tasks/<int:task_id>/status/",
        views.update_task_status,
        name="update_task_status"
    ),
    path(
        "api/tasks/<int:task_id>/delete/",
        views.delete_task_ajax,
        name="delete_task_ajax"
    ),

    # REST API подключаем после конкретных маршрутов
    path("api/", include(router.urls)),
]

