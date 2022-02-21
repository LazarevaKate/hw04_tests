from django.db import models
from django.contrib.auth import get_user_model
from django.shortcuts import reverse


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        db_index=True,
        verbose_name='URL'
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Вставьте описание группы'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:group_posts', kwargs={'slug': self.slug})


class Post(models.Model):
    text = models.TextField(
        help_text='Вставьте текст поста',
        verbose_name='Текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'

    )
    #image = models.ImageField(
        #'Картинка',
        #upload_to='posts/',
        #blank=True
    #)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    body = models.TextField()
    is_answered = models.BooleanField(default=False)
