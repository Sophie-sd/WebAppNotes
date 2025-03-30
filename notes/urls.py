from django.contrib import admin
from django.urls import path

from notes import views as notes_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('welcome/', notes_views.welcome, name='welcome'),  # Перша сторінка
    path('home/', notes_views.home, name='home'),  # Вхід у додаток

    path('', views.index, name='index'),  # <-- Важливо: тепер форма працює на /notes/

    path('delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('edit/<int:note_id>/', views.edit_note, name='edit_note'),
    path('ajax-add/', views.ajax_add_note, name='ajax_add_note'),
    path('trash/', views.trash, name='trash'),
    path('restore/<int:note_id>/', views.restore_note, name='restore_note'),
    path('permanent-delete/<int:note_id>/', views.permanent_delete, name='permanent_delete'),
    path('permanent-delete-all/', views.permanent_delete_all, name='permanent_delete_all'),
    path('trash/restore_all/', views.restore_all_notes, name='restore_all_notes'),
]
