from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
import logging
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Note, UserProfile, Folder
from .forms import UserProfileForm, NoteForm

logger = logging.getLogger(__name__)


def welcome(request):
    """Вітальна сторінка для неавтентифікованих користувачів."""
    if request.user.is_authenticated:
        return redirect('notes:home')
    return render(request, 'notes/welcome.html')


def login_register(request):
    """Обробляє логін та реєстрацію користувачів на одній сторінці."""
    if request.user.is_authenticated:
        return redirect('notes:home')

    if request.method == 'POST':
        # Логіка логіну
        if 'login-submit' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('notes:home')
            else:
                messages.error(request, 'Invalid login credentials.')
        # Логіка реєстрації
        elif 'register-submit' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email', '')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, email=email, password=password1)
                    login(request, user)
                    # Створюємо профіль для нового користувача
                    UserProfile.objects.create(user=user)
                    messages.success(request, 'Registration successful! You are now logged in.')
                    return redirect('notes:home')
                else:
                    messages.error(request, 'Username already exists.')
            else:
                messages.error(request, 'Passwords do not match.')

    return render(request, 'notes/login_register.html')


@login_required
def home(request):
    """Домашня сторінка для автентифікованих користувачів (після логіну)."""
    return render(request, 'notes/home.html')


def logout_view(request):
    """Виконує вихід користувача та перенаправляє на вітальну сторінку."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('welcome')


@login_required
def index(request):
    """Головна сторінка зі списком нотаток користувача, з можливістю фільтрації по папках."""
    # Отримуємо папки поточного користувача
    folders = Folder.objects.filter(user=request.user)

    # Перевіряємо, чи є параметр фільтрації по папці
    folder_filter_id = request.GET.get('folder')
    selected_folder = None

    notes_query = Note.objects.filter(user=request.user, is_deleted=False)

    if folder_filter_id:
        try:
            folder_filter_id = int(folder_filter_id)
            # Фільтруємо нотатки за обраною папкою
            notes_query = notes_query.filter(folder_id=folder_filter_id)
            selected_folder = Folder.objects.get(id=folder_filter_id, user=request.user)
        except (ValueError, Folder.DoesNotExist):
            # Якщо ID папки некоректний або папка не належить користувачу, показуємо всі нотатки
            folder_filter_id = None # Скидаємо фільтр
            notes_query = notes_query.filter(folder__isnull=True) # Або показуємо нотатки без папки?
            # Або взагалі не фільтруємо, якщо ID некоректний?
            # Вирішив показувати нотатки без папки при некоректному ID
    else:
        # Якщо папка не обрана, показуємо нотатки без папки
        notes_query = notes_query.filter(folder__isnull=True)

    notes = notes_query.order_by('-created_at')

    context = {
        'notes': notes,
        'folders': folders,
        'selected_folder_id': folder_filter_id,
        'selected_folder': selected_folder
    }
    return render(request, 'notes/index.html', context)


@login_required
def delete_note(request, note_id):
    """Переміщує нотатку до корзини (встановлює is_deleted=True)."""
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_deleted = True
    note.save()
    messages.info(request, f'Note "{note.title}" moved to trash.')
    return redirect('notes:index')


@login_required
def edit_note(request, note_id):
    """Обробляє редагування існуючої нотатки (тільки для власника)."""
    note = get_object_or_404(Note, id=note_id, user=request.user)

    if request.method == 'POST':
        # Передаємо user в форму для фільтрації папок
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            saved_note = form.save() # Зберігаємо, щоб отримати оновлений об'єкт
            messages.success(request, f'Note "{saved_note.title}" updated.')
            # Перенаправляємо на ту ж папку (або на index, якщо папки не було)
            redirect_url = reverse('notes:index')
            if saved_note.folder:
                redirect_url += f"?folder={saved_note.folder.id}"
            return redirect(redirect_url)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Передаємо user в форму для фільтрації папок
        form = NoteForm(instance=note, user=request.user)

    # Передаємо форму та ID нотатки в контекст
    return render(request, 'notes/edit_note.html', {'form': form, 'note_id': note_id})


@login_required
def ajax_add_note(request):
    """Обробляє AJAX POST-запит для створення нової нотатки."""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        folder_id = request.POST.get('folder') # Отримуємо ID папки
        folder_instance = None

        logger.info(f'AJAX Add Note: User {request.user.username}, Title: {title}, Folder ID: {folder_id}')

        # Знаходимо папку, якщо ID передано
        if folder_id:
            try:
                folder_instance = Folder.objects.get(id=folder_id, user=request.user)
            except (ValueError, Folder.DoesNotExist):
                logger.warning(f"Invalid folder ID {folder_id} received from user {request.user.username}")
                return JsonResponse({'error': 'Invalid folder specified.'}, status=400)

        if title and content:
            try:
                note = Note.objects.create(
                    user=request.user,
                    title=title,
                    content=content,
                    folder=folder_instance # Додаємо папку
                )
                logger.info(f'Note created with ID: {note.id} in folder: {folder_instance}')
                # Рендеримо картку нової нотатки
                html = render_to_string('notes/partials/note_card.html', {'note': note})
                return JsonResponse({'type': 'html', 'html': html})
            except Exception as e:
                logger.error(f"Error creating note for user {request.user.username}: {e}")
                return JsonResponse({'error': 'Error creating note.'}, status=500)
        else:
            logger.warning('AJAX Add Note: Title or content missing.')
            return JsonResponse({'error': 'Title and content are required'}, status=400)
    else:
        logger.warning(f'AJAX Add Note: Received {request.method} request from {request.user.username}')
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def trash(request):
    """Відображає список нотаток, переміщених до корзини."""
    notes = Note.objects.filter(user=request.user, is_deleted=True).order_by('-updated_at')
    return render(request, 'notes/trash.html', {'notes': notes})


@login_required
def restore_note(request, note_id):
    """Відновлює нотатку з корзини (встановлює is_deleted=False)."""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=True)
    note.is_deleted = False
    note.save()
    messages.success(request, f'Note "{note.title}" restored.')
    return redirect('notes:trash')


@login_required
def permanent_delete(request, note_id):
    """Остаточно видаляє нотатку з бази даних."""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=True)
    title = note.title # Зберігаємо назву для повідомлення
    note.delete()
    messages.success(request, f'Note "{title}" permanently deleted.')
    return redirect('notes:trash')


@login_required
def permanent_delete_all(request):
    """Остаточно видаляє всі нотатки користувача з корзини."""
    deleted_count, _ = Note.objects.filter(user=request.user, is_deleted=True).delete()
    messages.success(request, f'{deleted_count} notes permanently deleted from trash.')
    return redirect('notes:trash')


@login_required
def restore_all_notes(request):
    """Відновлює всі нотатки користувача з корзини."""
    restored_count = Note.objects.filter(user=request.user, is_deleted=True).update(is_deleted=False)
    messages.success(request, f'{restored_count} notes restored from trash.')
    return redirect('notes:trash')


@login_required
def delete_all_notes_forever(request):
    Note.objects.filter(user=request.user, is_deleted=True).delete()
    return redirect('notes:trash')


@login_required
def details_view(request, id):
    """Відображає детальну інформацію про нотатку в шаблоні."""
    note = get_object_or_404(Note, id=id, user=request.user)
    # Замість HttpResponse рендеримо шаблон
    context = {
        'note': note
    }
    return render(request, 'notes/note_detail.html', context)


@login_required
def profile_view(request):
    """Відображає та обробляє форму редагування профілю користувача."""
    # Використовуємо get_or_create для випадку, якщо профіль ще не створений (напр. для старих юзерів)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('notes:profile')
        else:
            # Якщо форма не валідна, помилки відобразяться в шаблоні
            messages.error(request, 'Please correct the errors below.')
    else:
        # Для GET-запиту показуємо форму, заповнену поточними даними
        form = UserProfileForm(instance=user_profile)

    return render(request, 'notes/profile.html', {'form': form})


@login_required
def search_notes(request):
    """Обробляє пошук нотаток за ключовим словом."""
    query = request.GET.get('q', '') # Отримуємо пошуковий запит
    notes = [] # Порожній список за замовчуванням

    if query:
        # Шукаємо тільки серед активних (не видалених) нотаток поточного користувача
        notes = Note.objects.filter(
            user=request.user,
            is_deleted=False
        ).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-updated_at') # Сортуємо за датою оновлення

        logger.info(f"User {request.user.username} searched for '{query}'. Found {notes.count()} notes.")
    else:
        # Якщо запит порожній, можна нічого не показувати або перенаправити кудись
        logger.info(f"User {request.user.username} submitted an empty search query.")
        # Можна додати повідомлення, якщо запит порожній
        # messages.info(request, "Please enter something to search for.")

    context = {
        'query': query,
        'notes': notes,
        'notes_count': notes.count() # Передаємо кількість знайдених нотаток
    }
    return render(request, 'notes/search_results.html', context)


@login_required
@require_POST # Тільки POST запити
def ajax_add_folder(request):
    """Обробляє AJAX-запит на створення нової папки."""
    folder_name = request.POST.get('name', '').strip()

    if not folder_name:
        return JsonResponse({'success': False, 'error': 'Folder name cannot be empty.'})
    
    # Перевірка на існування папки з такою ж назвою у цього користувача
    if Folder.objects.filter(user=request.user, name=folder_name).exists():
        return JsonResponse({'success': False, 'error': f'Folder "{folder_name}" already exists.'})

    try:
        new_folder = Folder.objects.create(user=request.user, name=folder_name)
        logger.info(f"User {request.user.username} created folder '{folder_name}' (ID: {new_folder.id}).")
        return JsonResponse({
            'success': True, 
            'folder': {
                'id': new_folder.id,
                'name': new_folder.name
            }
        })
    except Exception as e:
        logger.error(f"Error creating folder for user {request.user.username}: {e}")
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'})
