
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from dashboard.import_data import import_dashboard_data


class Command(BaseCommand):
    help = "Однократно переносит проекты, задачи и историю из JSON"

    def handle(self, *args, **options):
        file_path = Path("dashboard_data.json")

        if not file_path.exists():
            raise CommandError(
                "Файл dashboard_data.json не найден в корне проекта."
            )

        try:
            result = import_dashboard_data(file_path)
        except Exception as exc:
            raise CommandError(f"Импорт отменён: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Импорт завершён: "
                f"{result['projects']} проектов, "
                f"{result['tasks']} задач, "
                f"{result['activities']} записей истории."
            )
        )
