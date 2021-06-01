from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.view_template_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:<page>, доступен."""
        for view in self.view_template_names.keys():
            with self.subTest(view=view):
                response = self.guest_client.get(view)
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """При запросе к about:<page> применяется шаблон about/<page>.html."""
        for view, template in self.view_template_names.items():
            with self.subTest(view=view):
                response = self.guest_client.get(view)
                self.assertTemplateUsed(response, template)
