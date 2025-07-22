from django.test import TestCase, Client
from django.utils import timezone
from datetime import datetime
from .models import Task


# Create your tests here.


class SampleTestCase(TestCase):
    def test_sample(self):
        self.assertEqual(1 + 2, 3)


class TaskModelTestCase(TestCase):
    def test_create_task1(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
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
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title="task1", due_at=due)
        task.save()

        self.assertEqual(task.is_overdue(current), False)

    def test_is_overdue_past(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title="task1", due_at=due)
        task.save()

        self.assertEqual(task.is_overdue(current), True)

    def test_is_overdue_none(self):
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title="task1")
        task.save()

        self.assertEqual(task.is_overdue(current), False)


class TodoViewTestCase(TestCase):
    def test_index_get(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 0)

    def test_index_post(self):
        client = Client()
        data = {'title': 'task1', 'due_at': '2024-06-30 23:59:59'}
        response = client.post('/', data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(len(response.context['tasks']), 1)

    def test_index_get_order_post(self):
        task1 = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title="task2", due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()

        client = Client()
        response = client.get('/?order=post')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task2)
        self.assertEqual(response.context['tasks'][1], task1)

    def test_index_get_order_due(self):
        task1 = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title="task2", due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()

        client = Client()
        response = client.get('/?order=due')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/index.html')
        self.assertEqual(response.context['tasks'][0], task1)
        self.assertEqual(response.context['tasks'][1], task2)

    def test_detail_get_success(self):
        task = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)
    
    def test_detail_get_fail(self):
        client = Client()
        # 存在しないIDでアクセス
        response = client.get('/999/')

        self.assertEqual(response.status_code, 404)

    def test_close_success(self):
        task = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        self.assertEqual(task.completed, False)
        
        client = Client()
        response = client.get('/{}/close'.format(task.pk))
        
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(response.url, '/')
        
        task.refresh_from_db()
        self.assertEqual(task.completed, True)

    def test_close_fail(self):
        client = Client()
        # 存在しないIDでアクセス
        response = client.get('/999/close')
        
        self.assertEqual(response.status_code, 404)

    def test_update_get_success(self):
        task = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        
        client = Client()
        response = client.get('/{}/update'.format(task.pk))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/edit.html')
        self.assertEqual(response.context['task'], task)

    def test_update_get_fail(self):
        client = Client()
        # 存在しないIDでアクセス
        response = client.get('/999/update')
        
        self.assertEqual(response.status_code, 404)

    def test_update_post_success(self):
        task = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        
        client = Client()
        data = {'title': 'updated task', 'due_at': '2024-08-01 12:00:00'}
        response = client.post('/{}/update'.format(task.pk), data)
        
        self.assertEqual(response.status_code, 302)  # リダイレクト
        self.assertEqual(response.url, '/{}/'.format(task.pk))
        
        task.refresh_from_db()
        self.assertEqual(task.title, 'updated task')
        self.assertEqual(task.due_at, timezone.make_aware(datetime(2024, 8, 1, 12, 0, 0)))

    def test_update_post_fail(self):
        client = Client()
        data = {'title': 'updated task', 'due_at': '2024-08-01 12:00:00'}
        response = client.post('/999/update', data)
        
        self.assertEqual(response.status_code, 404)

    def test_delete_success(self):
        task = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        task_id = task.pk
        
        client = Client()
        response = client.get('/{}/delete'.format(task_id))
        
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(response.url, '/')
        
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=task_id)

    def test_delete_fail(self):
        client = Client()
        # 存在しないIDでアクセス
        response = client.get('/999/delete')
        
        self.assertEqual(response.status_code, 404)
