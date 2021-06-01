from .setup_tests import SetUpTests
from django.core.cache import cache


class URLTests(SetUpTests):
    def test_urls_exist_at_desired_location(self):
        """Страница доступна пользователю."""
        url_client_names = {
            '/': self.guest_client,
            f'/group/{self.group.slug}/': self.guest_client,
            f'/{self.creator.username}/': self.guest_client,
            '/new/': self.authorized_creator_client
        }

        for url, client in url_client_names.items():
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_template_names = {
            '/': 'index.html',
            f'/group/{self.group.slug}/': 'group.html',
            '/new/': 'new.html'
        }

        for url, template in url_template_names.items():
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_creator_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_edit_url_uses_correct_template(self):
        """URL-адрес /<username>/<post_id>/edit/ использует
           соответствующий шаблон."""
        response = self.authorized_creator_client.get(
            f'/{self.creator.username}/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'new.html')

    def test_edit_post_url_redirect_anonymous(self):
        """Страница /<username>/<post_id>/edit/ перенаправляет
           анонимного пользователя."""
        response = self.guest_client.get(
            f'/{self.creator.username}/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_post_url_redirect_anonymous_on_admin_login(self):
        """Страница /<username>/<post_id>/edit/ перенаправляет
           анонимного пользователя на страницу логина."""
        response = self.guest_client.get(
            f'/{self.creator.username}/{self.post.id}/edit/', follow=True)
        self.assertRedirects(response, (
            f'/auth/login/?next=/{self.creator.username}/{self.post.id}/edit/')
        )


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
