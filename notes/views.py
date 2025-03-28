# notes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Note

def welcome(request):
    return render(request, 'notes/welcome.html')

def home(request):
    return render(request, 'notes/home.html')

# Головна сторінка з формою + списком нотаток
def index(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Note.objects.create(title=title, content=content)
            return redirect('index')

    notes = Note.objects.order_by('-created_at')
    return render(request, 'notes/index.html', {'notes': notes})

# Видалення нотатки
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.delete()
    return redirect('index')

# Редагування нотатки
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    if request.method == 'POST':
        note.title = request.POST.get('title')
        note.content = request.POST.get('content')
        note.save()
        return redirect('index')

    return render(request, 'notes/edit_note.html', {'note': note})
