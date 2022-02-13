from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
            pub_date='13.02.22',
            group=cls.group
        )

    def setUp(self):
        self.user = User.objects.create_user(username='auth_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/post_create.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.client.get(reverse('posts:index'))
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_post, self.post)


class PaginatorViewsTest(TestCase):

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index'), {'page': '2'})
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_group_posts_show_correct_context(self):
        response = self.guest_client.get(
        reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        test_obj = response.context['page_obj'][0]
        test_text = response.context['text']
        test_group = response.context['group']
        test_author = str(test_obj.author)
        self.assertEqual(test_obj, self.post)
        self.assertEqual(str(test_author), 'author')
        self.assertEqual(test_text, 'some text')
        self.assertEqual(test_group, self.group)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'slug': self.user.username})
        )
        author = response.context['page_obj'][0]
        self.assertEqual(author['username'], 0)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_field_text = response.context['form'].initial['text']
        self.assertEqual(form_field_text, self.post.text)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response.context['post']
        author = self.author
        group = self.group
        text = 'Text for test'
        post_count = response.context['post_count']
        self.assertEqual(author, post.author)
        self.assertEqual(text, post.text)
        self.assertEqual(group, post.group)
        self.assertEqual(14, post_count)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_field_text = response.context['form'].initial['text']
        self.assertEqual(form_field_text, self.post.text)
