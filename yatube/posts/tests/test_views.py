from django import forms
from django.core.cache import cache
from django.urls import reverse

from posts.models import Follow, Group, Post
from posts.views import POSTS_PER_PAGE

from .setup_tests import SetUpTests

TOTAL_TEST_POSTS = 17
POST_CREATED_IN_SETUP = 1


class CommonPagesTests(SetUpTests):
    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates_names = {
            reverse('index'): 'index.html',
            reverse('group', kwargs=self.group_kwargs): 'group.html',
            reverse('new_post'): 'new.html',
            reverse('follow_index'): 'follow.html',
            reverse('profile', kwargs=self.creator_kwargs): 'profile.html',
            reverse('post', kwargs=self.post_kwargs): 'post.html',
            reverse('post_edit', kwargs=self.post_kwargs): 'new.html',
        }

        for url, template in pages_templates_names.items():
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_creator_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_pages_with_posts_paginator_show_correct_context(self):
        """Шаблон с пажинатором постов сформирован с правильным контекстом."""
        url_client_names = {
            reverse('index'): self.authorized_creator_client,
            reverse('follow_index'): self.authorized_follower_client,
            reverse('group', kwargs=self.group_kwargs):
                self.authorized_creator_client,
            reverse('profile', kwargs=self.creator_kwargs):
                self.authorized_creator_client
        }

        for url, client in url_client_names.items():
            with self.subTest(url=url):
                cache.clear()
                response = client.get(url)
                first_post = response.context['page'][0]
                self.assertEqual(self.post, first_post)

    def test_pages_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом."""
        url_context_names = {
            reverse('group', kwargs=self.group_kwargs):
                (self.group, 'group'),
            reverse('profile', kwargs=self.creator_kwargs):
                (self.creator, 'author')
        }

        for url, context in url_context_names.items():
            with self.subTest(url=url):
                response = self.authorized_creator_client.get(url)
                context_name = context[1]
                self.assertEqual(context[0], response.context[context_name])

    def test_pages_with_form_show_correct_context(self):
        """Шаблон с формой сформирован с правильным контекстом."""
        post_form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        comment_form_fields = {
            'text': forms.fields.CharField
        }

        url_form_field_names = {
            reverse('new_post'): post_form_fields,
            reverse('post_edit', kwargs=self.post_kwargs): post_form_fields,
            reverse('post', kwargs=self.post_kwargs): comment_form_fields,
            reverse('add_comment', kwargs=self.post_kwargs):
                comment_form_fields
        }

        for url, form_fields in url_form_field_names.items():
            response = self.authorized_creator_client.get(url, follow=True)

            for value, expected in form_fields.items():
                with self.subTest(url=url, value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_pages_show_correct_context(self):
        """Шаблон с постом сформирован с правильным контекстом."""
        url_names = {
            reverse('post', kwargs=self.post_kwargs),
            reverse('add_comment', kwargs=self.post_kwargs)
        }

        for url in url_names:
            response = self.authorized_creator_client.get(url, follow=True)
            post = response.context['post']
            self.assertEqual(self.post, post)

            creator = response.context['author']
            self.assertEqual(self.creator, creator)


class NewPostViewTests(SetUpTests):
    def test_new_post_shows_on_page(self):
        """Созданный пост попадает на страницу."""
        pages_clients_names = {
            reverse('index'): self.authorized_creator_client,
            reverse('group', kwargs=self.group_kwargs):
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
            reverse('group', kwargs=self.group_kwargs))

        for post in response.context.get('page').object_list:
            with self.subTest(post=post):
                self.assertNotEqual(post, new_post)


class NewCommentViewTests(SetUpTests):
    def test_new_comment_shows_on_page(self):
        """Созданный комментарий попадает на страницу."""
        response = self.authorized_creator_client.get(
            reverse('post', kwargs=self.post_kwargs)
        )
        comment = response.context.get('comments')[0]
        self.assertEqual(comment, self.comment)


class PaginatorViewTests(SetUpTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.pages_names = {
            reverse('index'),
            reverse('follow_index'),
            reverse('group', kwargs=cls.group_kwargs),
            reverse('profile', kwargs=cls.creator_kwargs)
        }

        for i in range(TOTAL_TEST_POSTS):
            cls.post = Post.objects.create(
                text='Тестовый пост ' + str(i),
                author=cls.creator,
                group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        """Первая страница пажинатора содержит POSTS_PER_PAGE записей."""
        for page in self.pages_names:
            with self.subTest(page=page):
                cache.clear()
                response = self.authorized_follower_client.get(page)
                self.assertEqual(len(
                    response.context.get('page').object_list), POSTS_PER_PAGE)

    def test_second_page_contains_seven_records(self):
        """Первая страница пажинатора содержит TOTAL_TEST_POSTS -
           POSTS_PER_PAGE + POST_CREATED_IN_SETUP записей."""
        for page in self.pages_names:
            with self.subTest(page=page):
                response = self.authorized_follower_client.get(
                    page + '?page=2')
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


class FollowTests(SetUpTests):
    def test_follow(self):
        """Фолловинг создаёт новую запись."""
        follow_count = Follow.objects.count()
        response = self.authorized_viewer_client.get(
            reverse('profile_follow', kwargs=self.creator_kwargs), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=response.wsgi_request.user,
                author=self.creator_kwargs['username']).exists())

    def test_unfollow(self):
        """Анфолловинг удаляет запись."""
        self.authorized_viewer_client.get(
            reverse('profile_follow', kwargs=self.creator_kwargs), follow=True)
        follow_count = Follow.objects.count()
        response = self.authorized_viewer_client.get(
            reverse('profile_unfollow', kwargs=self.creator_kwargs),
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=response.wsgi_request.user,
                author=self.creator_kwargs['username']).exists())
