from http import HTTPStatus

from django.test import TestCase


class CoreViewTestClass(TestCase):

    def test_error_page(self):
        response = self.client.get('/random_no_existing_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
