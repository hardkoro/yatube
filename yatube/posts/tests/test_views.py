from django.urls import reverse
from django import forms
from django.core.cache import cache

from .setup_tests import SetUpTests
from posts.models import Group, Post
from posts.views import POSTS_PER_PAGE

TOTAL_TEST_POSTS = 17
POST_CREATED_IN_SETUP = 1


class PostPagesTests(SetUpTests):
    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group', kwargs={'slug': self.group.slug})
            ),
            'new.html': reverse('new_post')
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_creator_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_post_context(self):
        """Шаблон сформирован с правильным контекстом постов."""
        url_names = {
            reverse('index'),
            reverse('group', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.creator.username})
        }

        for url in url_names:
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_creator_client.get(url)
                first_post = response.context['page'][0]
                self.assertEqual(PostPagesTests.post, first_post)

    def test_pages_show_correct_other_context(self):
        """Шаблон сформирован с правильным контекстом."""
        url_context_names = {
            reverse('group', kwargs={'slug': self.group.slug}):
                (PostPagesTests.group, 'group'),
            reverse('profile', kwargs={'username': self.creator.username}):
                (PostPagesTests.creator, 'author')
        }

        for url, context in url_context_names.items():
            with self.subTest(url=url):
                response = self.authorized_creator_client.get(url)
                context_name = context[1]
                self.assertEqual(context[0], response.context[context_name])

    def test_new_page_shows_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        url_names = {
            reverse('new_post'),
            reverse('post_edit',
                    kwargs={'username': self.creator.username,
                            'post_id': self.post.id})
        }

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for url in url_names:
            response = self.authorized_creator_client.get(url)

            for value, expected in form_fields.items():
                with self.subTest(url=url, value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_page_shows_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_creator_client.get(
            reverse('post', kwargs={'username': self.creator.username,
                                    'post_id': self.post.id}))
        post = response.context['post']
        self.assertEqual(PostPagesTests.post, post)

        creator = response.context['author']
        self.assertEqual(PostPagesTests.creator, creator)


class NewPostViewTests(SetUpTests):
    def test_new_post_shows_on_page(self):
        """Созданный пост попадает на страницу."""
        pages_clients_names = {
            reverse('index'): self.authorized_creator_client,
            reverse('group', kwargs={'slug': self.group.slug}):
                self.authorized_creator_client,
            reverse('follow_index'): self.authorized_follower_client}

        for reverse_name, client in pages_clients_names.items():
            with self.subTest(reverse_name=reverse_name, client=client):
                cache.clear()
                response = client.get(reverse_name)
                post = response.context.get('page').object_list[0]
                self.assertEqual(post, self.post)

    def test_new_post_does_not_show_on_unfollower_page(self):
        """Созданный пост не попадет в ленту не-фолловера."""
        response = self.authorized_viewer_client.get(reverse('follow_index'))
        post = response.context.get('page').object_list.count()
        self.assertNotEqual(post, self.post)

    def test_new_post_doesnt_show_on_other_group_page(self):
        """Созданный пост не попадает на страницу другой группы."""
        new_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2'
        )

        new_post = Post.objects.create(
            text='Тестовый пост 2',
            author=self.creator,
            group=new_group
        )

        response = self.authorized_creator_client.get(
            reverse('group', kwargs={'slug': self.group.slug}))

        for post in response.context.get('page').object_list:
            with self.subTest(post=post):
                self.assertNotEqual(post, new_post)


class PaginatorViewTests(SetUpTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        for i in range(TOTAL_TEST_POSTS):
            cls.post = Post.objects.create(
                text='Тестовый пост ' + str(i),
                author=cls.creator,
                group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        """Первая страница пажинатора содержит POSTS_PER_PAGE записей."""
        pages_names = {
            reverse('index'),
            reverse('group', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.creator.username})
        }

        for page in pages_names:
            cache.clear()
            response = self.client.get(page)
            self.assertEqual(len(
                response.context.get('page').object_list), POSTS_PER_PAGE)

    def test_second_page_contains_seven_records(self):
        """Первая страница пажинатора содержит TOTAL_TEST_POSTS -
           POSTS_PER_PAGE + POST_CREATED_IN_SETUP записей."""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(
            response.context.get('page').object_list),
            TOTAL_TEST_POSTS - POSTS_PER_PAGE + POST_CREATED_IN_SETUP)


class CacheTests(SetUpTests):
    def test_index_page_is_cached(self):
        """Новая запись на главной странице появится
           только после сброса кэша."""
        response = self.authorized_creator_client.get(reverse('index'))
        first_post_before = response.context['page'][0]

        self.post = Post.objects.create(
            text='Тестовый пост для кэша',
            author=self.creator
        )

        response = self.authorized_creator_client.get(reverse('index'))
        self.assertEqual(response.context, None)

        cache.clear()
        response = self.authorized_creator_client.get(reverse('index'))
        first_post_after = response.context['page'][0]
        self.assertNotEqual(first_post_before, first_post_after)
