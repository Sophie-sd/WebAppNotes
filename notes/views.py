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


@login_required
def index(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Note.objects.create(user=request.user, title=title, content=content)
            return redirect('index')

    notes = Note.objects.filter(user=request.user, is_deleted=False).order_by('-created_at')
    return render(request, 'notes/index.html', {'notes': notes})


@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_deleted = True
    note.save()
    return redirect('index')


@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.title = request.POST.get('title')
        note.content = request.POST.get('content')
        note.save()
        return redirect('index')
    return render(request, 'notes/edit_note.html', {'note': note})


@login_required
def ajax_add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        note = Note.objects.create(user=request.user, title=title, content=content)

        html = render_to_string('notes/partials/note_card.html', {'note': note})
        return JsonResponse({
            'type': 'html',
            'html': html
        })


@login_required
def trash(request):
    notes = Note.objects.filter(user=request.user, is_deleted=True).order_by('-updated_at')
    return render(request, 'notes/trash.html', {'notes': notes})


@login_required
def restore_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_deleted = False
    note.save()
    return redirect('trash')


@login_required
def permanent_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    return redirect('trash')


@login_required
def permanent_delete_all(request):
    Note.objects.filter(user=request.user, is_deleted=True).delete()
    return redirect('trash')


@login_required
def restore_all_notes(request):
    Note.objects.filter(user=request.user, is_deleted=True).update(is_deleted=False)
    return redirect('trash')


@login_required
def delete_all_notes_forever(request):
    Note.objects.filter(user=request.user, is_deleted=True).delete()
    return redirect('trash')


def details_view(request, id):
    note = get_object_or_404(Note, id=id)
    return render(request, 'notes/details.html', {'note': note})
