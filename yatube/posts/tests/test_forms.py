from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.non_author = User.objects.create_user(username='non_author')
        cls.group = Group.objects.create(
            title='test-group',
            description='test-name',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='text post',
            group=cls.group,
            pub_date='13.02.22'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth_user'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='text post'
            ).exists()
        )

    def test_text_valid_form_edit_post(self):
        post_count = Post.objects.count()
        old_post = self.post.text
        form_data = {
            'text': 'New post text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.get(id=self.post.id)
        self.assertNotEqual(response, old_post, new_post)
        self.assertNotEqual(Post.objects.count, post_count)

    def test_not_authorized_guest_has_redirect(self):
        post = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))
        self.assertEqual(Post.objects.count(), post)
