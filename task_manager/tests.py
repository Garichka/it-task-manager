from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Task, TaskType, Position


class SearchAndPaginationTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.position = Position.objects.create(name="Developer")

        self.user = self.user_model.objects.create_user(
            username="testuser",
            password="password123",
            position=self.position
        )

        self.task_type = TaskType.objects.create(name="Bug")
        for i in range(8):
            TaskType.objects.create(name=f"Type {i}")

        for i in range(8):
            Task.objects.create(
                name=f"Task {i}",
                description="Test description",
                deadline="2026-12-31",
                priority="Medium",
                task_type=self.task_type
            )

        for i in range(8):
            self.user_model.objects.create_user(
                username=f"worker_{i}",
                password="password123",
                position=self.position
            )

    def test_workers_search_logic(self):
        self.client.login(username="testuser", password="password123")
        url = reverse("task_manager:worker-list")
        response = self.client.get(url, {"queryset": "worker"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["worker_list"]), 5)
        self.assertEqual(response.context["paginator"].count, 8)
        self.assertContains(response, 'value="worker"')

    def test_tasks_search_logic(self):
        self.client.login(username="testuser", password="password123")
        url = reverse("task_manager:task-list")
        response = self.client.get(url, {"queryset": "task"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["task_list"]), 5)
        self.assertEqual(response.context["paginator"].count, 8)
        self.assertContains(response, "queryset=task")
        self.assertContains(response, "page=2")

    def test_task_types_search_logic(self):
        self.client.login(username="testuser", password="password123")
        url = reverse("task_manager:task-type-list")
        response = self.client.get(url, {"queryset": "TYPE"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["task_type_list"]), 5)
        self.assertEqual(response.context["paginator"].count, 8)
        self.assertContains(response, 'value="TYPE"')

    def test_empty_search_returns_all_results(self):
        self.client.login(username="testuser", password="password123")

        url_workers = reverse("task_manager:worker-list")
        res_workers = self.client.get(url_workers, {"queryset": ""})
        self.assertEqual(res_workers.context["paginator"].count, 9)

        url_tasks = reverse("task_manager:task-list")
        res_tasks = self.client.get(url_tasks, {"queryset": ""})
        self.assertEqual(res_tasks.context["paginator"].count, 8)

        url_types = reverse("task_manager:task-type-list")
        res_types = self.client.get(url_types, {"queryset": ""})
        self.assertEqual(res_types.context["paginator"].count, 9)

    def test_anonymous_user_redirect(self):
        urls = [
            reverse("task_manager:worker-list"),
            reverse("task_manager:task-list"),
            reverse("task_manager:task-type-list")
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/accounts/login/?next={url}")
