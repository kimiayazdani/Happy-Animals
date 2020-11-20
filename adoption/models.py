from django.contrib.postgres.fields import ArrayField
from django.db import models

from _helpers.db import TimeModel
from account_management.models import Account


class Post(TimeModel):
    KIND_DOG = 'dog'
    KIND_CAT = 'cat'
    KIND_HAMSTER = 'hamster'

    KIND_CHOICES = (
        (KIND_DOG, 'سگ'),
        (KIND_CAT, 'گربه'),
        (KIND_HAMSTER, 'همستر'),
    )

    KINDS = tuple(dict(KIND_CHOICES).keys())

    title = models.CharField(max_length=255, verbose_name='عنوان')
    kind = models.CharField(
        choices=KIND_CHOICES, default=KIND_DOG, max_length=20, db_index=True, verbose_name='نوع حیوان خانگی'
    )
    description = models.TextField(verbose_name='توضیحات')
    author = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='نویسنده')
    pet_image = models.ImageField(upload_to="", blank=True, verbose_name='تصویر')
    tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'animals_post'
        verbose_name = 'پست'
        verbose_name_plural = 'پست‌ها'


class Comment(TimeModel):
    author = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='نویسنده')
    content = models.TextField(verbose_name='محتوا')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='پست')

    def __str__(self):
        return self.post.title + '/' + self.author.username

    class Meta:
        db_table = 'animals_comment'
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت‌ها'
