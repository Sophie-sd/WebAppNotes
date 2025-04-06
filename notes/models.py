from django.contrib.auth.models import User
from django.db import models

# Модель для папок
class Folder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Унікальність назви папки для одного користувача
        unique_together = ('user', 'name')
        ordering = ['name'] # Сортування за замовчуванням

    def __str__(self):
        return self.name

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    # Зв'язок з папкою (дозволяємо нотаткам бути без папки)
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    content = models.TextField(verbose_name="Текст нотатки")
    created_at = models.DateTimeField(verbose_name="Дата створення", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Оновлено", auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.user.username
