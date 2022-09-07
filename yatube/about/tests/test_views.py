from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_uses_correct_templates(self):
        """Проверка корректных шаблонов страниц about"""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_about_author_page_uses_correct_template(self):
        """Проверка корректного шаблона страницы about/author"""
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')
