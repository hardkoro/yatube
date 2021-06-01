from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.url_template_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

    def test_about_urls_exist_at_desired_location(self):
        for url in self.url_template_names.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_urls_uses_correct_template(self):
        for url, template in self.url_template_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
