import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string

from .models import Note


def welcome(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'notes/welcome.html')


def login_register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            # Login
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials')

        elif 'password1' in request.POST:
            # Register
            username = request.POST['username']
            email = request.POST.get('email', '')
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 == password2:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, email=email, password=password1)
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'Username already exists')
            else:
                messages.error(request, 'Passwords do not match')

    return render(request, 'notes/login_register.html')


@login_required
def home(request):
    return render(request, 'notes/home.html')


def logout_view(request):
    logout(request)
    return redirect('welcome')


def index(request):
    if not request.user.is_authenticated:
        return redirect('login_register')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Note.objects.create(title=title, content=content)
            return redirect('index')

    notes = Note.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'notes/index.html', {'notes': notes})


def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.is_deleted = True
    note.save()
    return redirect('index')


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
            return JsonResponse({
                'type': 'json',
                'note': {
                    'title': note.title,
                    'content': note.content,
                }
            })
        else:
            html = render_to_string('notes/partials/note_card.html', {'note': note})
            return JsonResponse({
                'type': 'html',
                'html': html
            })


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
