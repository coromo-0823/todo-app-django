from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Todo
from .forms import TodoForm

@login_required
def todo_list(request):
    search_query = request.GET.get('search', '')
    filter_status = request.GET.get('status', 'all')
    
    todos = Todo.objects.filter(user=request.user)
    
    if search_query:
        todos = todos.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if filter_status == 'completed':
        todos = todos.filter(completed=True)
    elif filter_status == 'pending':
        todos = todos.filter(completed=False)
    
    context = {
        'todos': todos,
        'search_query': search_query,
        'filter_status': filter_status,
    }
    return render(request, 'todo/todo_list.html', context)

@login_required
def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            messages.success(request, 'タスクが作成されました。')
            return redirect('todo_list')
    else:
        form = TodoForm()
    
    return render(request, 'todo/todo_form.html', {'form': form, 'title': 'タスク作成'})

@login_required
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'タスクが更新されました。')
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    
    return render(request, 'todo/todo_form.html', {'form': form, 'title': 'タスク編集'})

@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'タスクが削除されました。')
        return redirect('todo_list')
    
    return render(request, 'todo/todo_confirm_delete.html', {'todo': todo})

@login_required
def todo_toggle(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.completed = not todo.completed
    todo.save()
    
    status = '完了' if todo.completed else '未完了'
    messages.success(request, f'タスクを{status}に変更しました。')
    return redirect('todo_list')