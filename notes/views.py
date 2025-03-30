# notes/views.py

import random

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

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

    notes = Note.objects.filter(is_deleted=False).order_by('-created_at')
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


def ajax_add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        note = Note.objects.create(title=title, content=content)

        if random.choice([True, False]):
            # Повертаємо JSON
            return JsonResponse({
                'type': 'json',
                'note': {
                    'title': note.title,
                    'content': note.content,
                }
            })
        else:
            # Повертаємо готовий HTML
            html = render_to_string('notes/partials/note_card.html', {'note': note})
            return JsonResponse({
                'type': 'html',
                'html': html
            })


# Переміщення нотатки в корзину замість видалення
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.is_deleted = True
    note.save()
    return redirect('index')


# Корзина
def trash(request):
    notes = Note.objects.filter(is_deleted=True).order_by('-updated_at')
    return render(request, 'notes/trash.html', {'notes': notes})


def restore_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.is_deleted = False
    note.save()
    return redirect('trash')


def permanent_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.delete()
    return redirect('trash')


def permanent_delete_all(request):
    Note.objects.filter(is_deleted=True).delete()
    return redirect('trash')


def restore_all_notes(request):
    Note.objects.filter(is_deleted=True).update(is_deleted=False)
    return redirect('trash')


def delete_all_notes_forever(request):
    Note.objects.filter(is_deleted=True).delete()
    return redirect('trash')
