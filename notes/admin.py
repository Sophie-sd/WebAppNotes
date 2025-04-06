from django.contrib import admin
from .models import Note, UserProfile, Folder

# Налаштування для кращого відображення в адмінці (опціонально)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'is_deleted')
    list_filter = ('is_deleted', 'user')
    search_fields = ('title', 'content')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'birth_date', 'gender')
    search_fields = ('user__username', 'full_name')

# Налаштування для Folder
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('name', 'user__username')

admin.site.register(Note, NoteAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Folder, FolderAdmin)
