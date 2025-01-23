# myapp/views.py
from django.shortcuts import render
from .models import Task



from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm

def home(request):
    # You can pass data to the template using context
    tasks = Task.objects.all()
    context = {
        'app_name': 'My Todo App',
        'tasks':tasks,
    }
    return render(request, 'task/base.html', context)



def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the home page or task list
    else:
        form = TaskForm()

    return render(request, 'task/add_task.html', {'form': form})


from django.shortcuts import get_object_or_404, redirect
from .models import Task

def change_task_status(request, task_id, new_status):
    # Fetch the task by ID
    task = get_object_or_404(Task, id=task_id)
    
    # Update the status
    task.status = new_status
    task.save()
    
    # Redirect back to the task list or any other page
    return redirect('home')

from django.shortcuts import get_object_or_404, redirect
from .models import Task

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('home')  # Redirect back to the task list


from django.shortcuts import render, get_object_or_404
from .models import Task

from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from .forms import TaskForm  # Assuming you have a TaskForm

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', task_id=task.id)  # Redirect to the updated task detail page
    else:
        form = TaskForm(instance=task)  # Pre-fill the form with the current task data

    return render(request, 'task/task_detail.html', {'task': task, 'form': form})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from .forms import TaskForm  # Assuming you have a TaskForm

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)  # Get the task by ID
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)  # Bind the form with the existing task data
        if form.is_valid():
            form.save()  # Save the updated task data
            return redirect('task_detail', task_id=task.id)  # Redirect to the task detail page after saving
    else:
        form = TaskForm(instance=task)  # Pre-fill the form with the task's existing data
    return render(request, 'task/edit_task.html', {'form': form, 'task': task})






