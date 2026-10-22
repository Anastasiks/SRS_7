
from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название проекта"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("pending", "На согласовании"),
        ("assigned", "Назначена"),
        ("rejected", "Отклонена"),
        ("in_progress", "В работе"),
        ("done", "Завершена"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Низкий"),
        ("medium", "Средний"),
        ("high", "Высокий"),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Название"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Проект"
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_tasks",
        null=True,
        blank=True,
        verbose_name="Автор задачи"
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
        verbose_name="Исполнитель"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус"
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="Приоритет"
    )

    deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дедлайн"
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Причина отклонения"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    def __str__(self):
        return self.title


class Activity(models.Model):
    EVENT_CHOICES = [
        ("created", "Создание"),
        ("submitted", "Отправка на согласование"),
        ("approved", "Согласование"),
        ("rejected", "Отклонение"),
        ("assigned", "Назначение исполнителя"),
        ("started", "Начало работы"),
        ("completed", "Завершение"),
        ("updated", "Изменение"),
        ("deleted", "Удаление"),
    ]

    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        related_name="activities",
        null=True,
        blank=True,
        verbose_name="Задача"
    )

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_CHOICES,
        default="updated",
        verbose_name="Тип события"
    )

    description = models.CharField(
        max_length=255,
        verbose_name="Описание события"
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_activities",
        verbose_name="Инициатор"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата события"
    )

    def __str__(self):
        return self.description
