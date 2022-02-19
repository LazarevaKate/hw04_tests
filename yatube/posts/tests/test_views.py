from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group
from ..views import POST_COUNT

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
            group=cls.group
        )

    def setUp(self):
        self.user = User.objects.create_user(username='auth_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)
        self.new_group = Group.objects.create(
            title='Test title',
            description='Test description',
            slug='slug-test'
        )

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
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_group_posts_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        test_object = response.context['page_obj'][0]
        text = test_object.text
        group = test_object.group.title
        contexts = {
            text: 'Тестовый текст',
            group: self.group.title
        }
        for context, expected in contexts.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',kwargs={'username': self.post_author.username})
        )
        self.assertTrue(
            response.context['author'] == PostsPagesTests.post_author, 0
        )

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        is_edit = response.context.get('is_edit')
        self.assertIsNone(is_edit, PostForm)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        author = first_object.author
        group = first_object.group
        text = first_object.text
        contexts = {
            author: self.post_author,
            text: 'Тестовый текст',
            group: self.group
        }
        for context, expected in contexts.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_post_on_page(self):
        paths = [
            reverse('posts:index'),
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:profile',
                    kwargs={'username': self.post_author.username}
                    ),
        ]
        for path in paths:
            response = self.authorized_client.get(path)
            posts = response.context['page_obj'][0]
            self.assertEqual(posts.text, PostsPagesTests.post.text)
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_has_correct_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertFalse(Post.objects.filter(
            id=self.post.id,
            text='Какой-то текст',
            group=self.new_group.id).exists()
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='pagin_test')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )

    def setUp(self):
        self.post_count = 13
        posts = (Post(
            text=f'Тестовый текст {i}',
            author=self.post_author,
            pub_date='13.02.22',
            group=self.group
        )for i in range(self.post_count))

        Post.objects.bulk_create(posts)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), POST_COUNT)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index'), {'page': 2})
        second_page = Post.objects.count() % POST_COUNT
        self.assertEqual(len(response.context['page_obj']), second_page)

    def test_group_list_has_page(self):
        response = self.client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), POST_COUNT)

    def test_profile_has_page(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': self.post_author.username})
        )
        self.assertEqual(len(response.context['page_obj']), POST_COUNT)
