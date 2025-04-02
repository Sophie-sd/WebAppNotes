from django.contrib.auth.models import User
from django.db import models


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    content = models.TextField(verbose_name="Текст нотатки")
    created_at = models.DateTimeField(verbose_name="Дата створення", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Оновлено", auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
