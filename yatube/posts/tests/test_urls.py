from .setup_tests import SetUpTests
from django.core.cache import cache


class URLTests(SetUpTests):
    def test_urls_exist_at_desired_location(self):
        """Страница доступна пользователю."""
        url_client_names = {
            '/': self.guest_client,
            f'/group/{self.group.slug}/': self.guest_client,
            f'/{self.creator.username}/': self.guest_client,
            '/new/': self.authorized_creator_client,
            f'/{self.creator.username}/follow/':
                self.authorized_creator_client,
            f'/{self.creator.username}/unfollow/':
                self.authorized_creator_client,
            f'/{self.creator.username}/{self.post.id}/comment/':
                self.authorized_creator_client
        }

        for url, client in url_client_names.items():
            with self.subTest(client=client):
                response = client.get(url, follow=True)
                self.assertEqual(response.status_code, 200)

    def test_url_is_not_available_for_guest_user(self):
        """Страница не доступа не залогиненному пользователю."""
        url_names = {
            '/new/',
            f'/{self.creator.username}/follow/',
            f'/{self.creator.username}/unfollow/',
            f'/{self.creator.username}/{self.post.id}/comment/'
        }

        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 302)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_template_names = {
            '/': 'index.html',
            f'/group/{self.group.slug}/': 'group.html',
            '/new/': 'new.html',
            f'/{self.creator.username}/{self.post.id}/edit/': 'new.html'
        }

        for url, template in url_template_names.items():
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_creator_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_redirects_anonymous_on_admin_login(self):
        """Страница перенаправляет анонимного пользователя
           на страницу логина."""
        url_list = {
            '/edit/',
            '/comment/'
        }

        for url in url_list:
            full_url = f'/{self.creator.username}/{self.post.id}' + url

            with self.subTest(full_url=full_url):
                response = self.guest_client.get(full_url)
                self.assertEqual(response.status_code, 302)
                response = self.guest_client.get(full_url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={full_url}')


class PostURLTests(SetUpTests):
    def test_post_edit_url_doesnt_exist_for_guest_user(self):
        """Страница /<username>/<post_id>/edit/ доступна
           только автору поста."""
        client_status_code_names = {
            self.guest_client: 302,
            self.authorized_viewer_client: 302,
            self.authorized_creator_client: 200
        }

        for client, status_code in client_status_code_names.items():
            with self.subTest(client=client):
                response = client.get(
                    f'/{self.creator.username}/{self.post.id}/edit/')
                self.assertEqual(response.status_code, status_code)


class NotFoundURLTest(SetUpTests):
    def test_not_found_url_returns_404(self):
        """Не существующая страница вернёт 404."""
        response = self.guest_client.get('/not-found/')
        self.assertEqual(response.status_code, 404)
