from django.db import models
from account.models import AbstractUser as User
from afiche import settings

from django.utils import timezone


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class BookDirection(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.name}'


class Genre(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f'{self.name}'


class Book(models.Model):
    author_account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books', null=True, blank=True)

    author = models.CharField(max_length=80)
    title = models.CharField(max_length=320)
    description = models.TextField(max_length=2000)

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='books', null=True)
    direction = models.ForeignKey(BookDirection, on_delete=models.CASCADE, related_name='books')

    pages = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    pdf = models.FileField(upload_to='books/%Y')

    image1 = models.ImageField(upload_to=f'media/images/', null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.title} ({str(self.year)}/{self.pages})"

    def get_image_url(self, field_name):
        try:
            image_field = getattr(self, field_name)
            if image_field:
                return f"{settings.LINK}{image_field.url}"
            else:
                return 'Image Not Found'
        except ValueError:
            return 'Image Not Found'

    def get_pdf_url(self):
        try:
            pdf = getattr(self, 'pdf')
            if pdf:
                return f"{settings.LINK}{pdf.url}"
            else:
                return 'PDF Not Found'
        except ValueError:
            return 'PDF Not Found'



class ViewsStats(models.Model):
    user = models.ForeignKey(User, related_name='view_stats', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='view_stats', on_delete=models.CASCADE)
    d_count = models.BooleanField(default=False)
    v_count = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.user.email} -> {self.book.title}'


class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='favorites', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.email} -> {self.book.title}'


class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(max_length=500)

    def __str__(self) -> str:
        if self.user:
            return f'{self.user.email} -> {self.book.title}'
        else:
            return 'deleted or someone'


class News(models.Model):
    author_account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news', null=True, blank=True)

    title = models.CharField(max_length=320)
    description = models.TextField(max_length=2000)

    news_date = models.DateTimeField(default=timezone.now)

    image1 = models.ImageField(upload_to=f'media/images/', null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.title}"

    def get_image_url(self, field_name):
        try:
            image_field = getattr(self, field_name)
            if image_field:
                return image_field.url
            else:
                return 'Image Not Found'
        except ValueError:
            return 'Image Not Found'
