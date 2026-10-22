
from rest_framework import serializers
from .models import Project, Task, Activity


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )
    owner_name = serializers.CharField(
        source="owner.username",
        read_only=True,
        default=""
    )
    assignee_name = serializers.CharField(
        source="assignee.username",
        read_only=True,
        default=""
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "project",
            "project_name",
            "owner",
            "owner_name",
            "assignee",
            "assignee_name",
            "status",
            "priority",
            "deadline",
            "rejection_reason",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "status",
            "rejection_reason",
            "created_at",
        ]

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Название задачи не может быть пустым."
            )
        return value.strip()


class ActivitySerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(
        source="actor.username",
        read_only=True,
        default="Система"
    )

    class Meta:
        model = Activity
        fields = [
            "id",
            "task",
            "event_type",
            "description",
            "actor",
            "actor_name",
            "created_at",
        ]
        read_only_fields = fields
