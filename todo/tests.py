from django.test import TestCase
from django.utils import timezone
from datetime import datetime
from .models import Task

# Create your tests here.
class SampleTestCase(TestCase):
    def test_sample(self):
        self.assertEqual(1 + 2, 3)

class TaskModelTestCase(TestCase):
    def test_create_task1(self):
        due = timezone.make_aware(datetime(2024,6,30,23,59,59))
        task = Task(title="task1", due_at=due)
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, "task1")
        self.assertEqual(task.completed, False)
        self.assertEqual(task.due_at, due)

    def test_create_task2(self):
        task = Task(title="task2")
        task.save()
        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, "task2")
        self.assertEqual(task.completed, False)
        self.assertEqual(task.due_at, None)

    def test_is_overdue_future(self):
        due = timezone.make_aware(datetime(2024,6,30,23,59,59))
        current = timezone.make_aware(datetime(2024,6,30,0,0,0))
        task = Task(title="task1", due_at=due)
        task.save()

        self.assertEqual(task.is_overdue(current), False)

    def test_is_overdue_past(self):
        due = timezone.make_aware(datetime(2024,6,30,23,59,59))
        current = timezone.make_aware(datetime(2024,7,1,0,0,0))
        task = Task(title="task1", due_at=due)
        task.save()

        self.assertEqual(task.is_overdue(current), True)
    
    def test_is_overdue_none(self):
        current = timezone.make_aware(datetime(2024,7,1,0,0,0))
        task = Task(title="task1")
        task.save()

        self.assertEqual(task.is_overdue(current), False)
