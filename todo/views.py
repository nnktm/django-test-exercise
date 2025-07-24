from django.shortcuts import render, redirect
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from .models import Task
from django.http import Http404
from django.utils import timezone
# Create your views here.


def index(request):
    if request.method == 'POST':
        task = Task(title=request.POST['title'],
                    subject=request.POST.get('subject'),
                    due_at=make_aware(parse_datetime(request.POST['due_at'])))
        task.save()
        return redirect(index)
    tasks = Task.objects.all()
    subjects = Task.objects.exclude(subject__isnull=True).exclude(subject__exact='').values_list('subject', flat=True).distinct()

    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')

    today = timezone.now()

    context = {'tasks': tasks,
               'today': today
    }
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    
    context = {'task': task}

    return render(request, 'todo/detail.html', context)


def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)

def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task does not exist')
    if request.method == 'POST':
        task.title = request.POST['title']
        task.subject = request.POST.get('subject')
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task
    }
    return render(request, 'todo/edit.html', context)

def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)
