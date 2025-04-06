from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from notes import views as notes_views

app_name = 'notes'

urlpatterns = [
    # Адмінка
    path('admin/', admin.site.urls),

    # Основні сторінки
    path('', notes_views.welcome, name='welcome'),  # перший екран
    path('login/', notes_views.login_register, name='login_register'),  # форма входу/реєстрації
    path('home/', notes_views.home, name='home'),  # домашня сторінка

    # Нотатки
    path('notes/', notes_views.index, name='index'),  # головна з нотатками
    path('delete/<int:note_id>/', notes_views.delete_note, name='delete_note'),
    path('edit/<int:note_id>/', notes_views.edit_note, name='edit_note'),
    path('ajax-add/', notes_views.ajax_add_note, name='ajax_add_note'),
    path('note/<int:id>/', notes_views.details_view, name='details'),

    # Пошук
    path('search/', notes_views.search_notes, name='search_notes'),

    # Папки (AJAX)
    path('ajax-add-folder/', notes_views.ajax_add_folder, name='ajax_add_folder'),

    # Корзина
    path('trash/', notes_views.trash, name='trash'),
    path('restore/<int:note_id>/', notes_views.restore_note, name='restore_note'),
    path('permanent-delete/<int:note_id>/', notes_views.permanent_delete, name='permanent_delete'),
    path('permanent-delete-all/', notes_views.permanent_delete_all, name='permanent_delete_all'),
    path('trash/restore_all/', notes_views.restore_all_notes, name='restore_all_notes'),

    # Вихід
    path('logout/', notes_views.logout_view, name='logout'),

    # Профіль та зміна пароля
    path('profile/', notes_views.profile_view, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='notes/password_change_form.html', success_url='/notes/password_change/done/'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='notes/password_change_done.html'), name='password_change_done'),
]
