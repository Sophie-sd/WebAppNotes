from django.db import models

class Note(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Текст нотатки")
    created_at = models.DateTimeField("Дата створення", auto_now_add=True)
    updated_at = models.DateTimeField("Оновлено", auto_now=True)

    def __str__(self):
        return self.title
