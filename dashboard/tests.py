
from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch

from .models import Project, Task, Activity


class TaskTransactionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="transaction_test",
            password="test_password_123"
        )

        self.project = Project.objects.create(
            name="Тестовый проект",
            description="Проверка транзакций"
        )

        self.task = Task.objects.create(
            title="Тестовая задача",
            description="Проверка отката",
            project=self.project,
            owner=self.user,
            status="new",
            priority="medium"
        )

    @patch("dashboard.views.Activity.objects.create")
    def test_transition_rolls_back_if_history_creation_fails(
        self, mock_activity_create
    ):
        mock_activity_create.side_effect = Exception(
            "Ошибка записи истории"
        )

        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user)
        client.raise_request_exception = False

        response = client.post(
            f"/api/tasks/{self.task.id}/transition/",
            {"status": "pending"},
            format="json"
        )

        self.task.refresh_from_db()

        self.assertEqual(self.task.status, "new")
        self.assertEqual(Activity.objects.count(), 0)
        self.assertEqual(response.status_code, 500)
