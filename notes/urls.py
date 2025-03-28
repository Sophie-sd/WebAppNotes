from django.contrib import admin
from django.urls import path, include
from notes import views as notes_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('welcome/', notes_views.welcome, name='welcome'),  # Перша сторінка
    path('home/', notes_views.home, name='home'),           # Вхід у додаток

    path('', views.index, name='index'),  # <-- Важливо: тепер форма працює на /notes/

    path('delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('edit/<int:note_id>/', views.edit_note, name='edit_note'),
]