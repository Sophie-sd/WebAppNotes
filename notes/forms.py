from django import forms
from .models import UserProfile, Note, Folder # Додамо Note, якщо знадобиться форма для нотаток

class UserProfileForm(forms.ModelForm):
    """Форма для редагування профілю користувача."""
    class Meta:
        model = UserProfile
        # Виключаємо поле 'user', оскільки воно встановлюється автоматично
        # Додаємо 'bio' до полів, які редагуються
        fields = ['full_name', 'birth_date', 'gender', 'avatar', 'bio']
        widgets = {
            # Використовуємо HTML5 віджет для дати
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            # Робимо поле bio трохи більшим
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us a little about yourself...'}),
            # Додамо плейсхолдер для імені
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            # Можна додати атрибути і для інших полів, якщо потрібно
            'gender': forms.Select(),
            'avatar': forms.ClearableFileInput(), # Використовуємо стандартний віджет для файлів
        }
        labels = {
            # Можна перевизначити стандартні мітки полів для ясності
            'full_name': 'Full Name',
            'birth_date': 'Date of Birth',
            'gender': 'Gender',
            'avatar': 'Profile Picture',
            'bio': 'About Me',
        }
        help_texts = {
             'avatar': 'Upload a new picture for your profile.',
             # Можна додати підказки для інших полів
        }

# Форма для створення/редагування нотаток
class NoteForm(forms.ModelForm):
    """Форма для створення та редагування нотаток."""
    class Meta:
        model = Note
        # Включаємо поля, які редагує користувач + нове поле папки
        fields = ['title', 'content', 'folder']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Note title', 'class': 'note-edit-title'}),
            'content': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Note content...', 'class': 'note-edit-content'}),
            # Налаштуємо віджет для папки, щоб показати папки поточного користувача
            'folder': forms.Select(),
        }
        labels = {
            'title': 'Title',
            'content': 'Content',
            'folder': 'Folder (Optional)',
        }

    # Налаштовуємо поле folder, щоб показувати тільки папки поточного користувача
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['folder'].queryset = Folder.objects.filter(user=user)
            self.fields['folder'].required = False # Робимо поле необов'язковим

# Потенційно, форма для створення/редагування нотаток (якщо не використовувати AJAX)
# class NoteForm(forms.ModelForm):
#     class Meta:
#         model = Note
#         fields = ['title', 'content']
#         widgets = {
#             'title': forms.TextInput(attrs={'placeholder': 'Note title'}),
#             'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Note content...'}),
#         }