from django.test import TestCase

from ..models import User, Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Какой-то текст',
            author=cls.user,
            pub_date='13.02.22',
            group=cls.group,
        )

    def test_models(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='auth_2')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Тут текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='текст',
            author=cls.post_author
        )

    def test_models(self):
        group = GroupModelTest.group
        object_name = group.title
        self.assertEqual(object_name, str(group))
