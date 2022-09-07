from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutUrlTest(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_location(self):
        urls = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for address, status in urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)
