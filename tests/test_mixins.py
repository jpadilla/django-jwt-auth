import pytest
from django.test import TestCase
from django.test.client import Client

from jwt_auth import utils
from jwt_auth.compat import User, json, smart_text


@pytest.mark.django_db
class JSONWebTokenAuthMixinTestCase(TestCase):
    def setUp(self):
        self.email = 'jpueblo@example.com'
        self.username = 'jpueblo'
        self.password = 'password'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.data = {
            'username': self.username,
            'password': self.password
        }

        self.client = Client()

    def test_post_json_passing_jwt_auth(self):
        """
        Ensure POSTing form over JWT auth with correct credentials
        passes and does not require CSRF
        """
        payload = utils.jwt_payload_handler(self.user)
        token = utils.jwt_encode_handler(payload)

        auth = 'Bearer {0}'.format(token)
        response = self.client.post(
            '/jwt/',
            content_type='application/json',
            HTTP_AUTHORIZATION=auth
        )

        response_content = json.loads(smart_text(response.content))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content['username'], self.username)

    def test_post_json_failing_jwt_auth(self):
        """
        Ensure POSTing json over JWT auth without correct credentials fails
        """
        response = self.client.post('/jwt/', content_type='application/json')

        response_content = json.loads(smart_text(response.content))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'JWT realm="api"')

        expected_error = ['Incorrect authentication credentials.']
        self.assertEqual(response_content['errors'], expected_error)

    def test_post_no_jwt_header_failing_jwt_auth(self):
        """
        Ensure POSTing over JWT auth without credentials fails
        """
        auth = 'Bearer'
        response = self.client.post(
            '/jwt/',
            content_type='application/json',
            HTTP_AUTHORIZATION=auth,
        )

        response_content = json.loads(smart_text(response.content))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'JWT realm="api"')

        expected_error = ['Invalid Authorization header. No credentials provided.']
        self.assertEqual(response_content['errors'], expected_error)

    def test_post_invalid_jwt_header_failing_jwt_auth(self):
        """
        Ensure POSTing over JWT auth without correct credentials fails
        """
        auth = 'Bearer abc abc'
        response = self.client.post(
            '/jwt/',
            content_type='application/json',
            HTTP_AUTHORIZATION=auth
        )

        response_content = json.loads(smart_text(response.content))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'JWT realm="api"')

        expected_error = ['Invalid Authorization header. Credentials string should not contain spaces.']
        self.assertEqual(response_content['errors'], expected_error)

    def test_post_expired_token_failing_jwt_auth(self):
        """
        Ensure POSTing over JWT auth with expired token fails
        """
        payload = utils.jwt_payload_handler(self.user)
        payload['exp'] = 1
        token = utils.jwt_encode_handler(payload)

        auth = 'Bearer {0}'.format(token)
        response = self.client.post(
            '/jwt/',
            content_type='application/json',
            HTTP_AUTHORIZATION=auth
        )

        response_content = json.loads(smart_text(response.content))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'JWT realm="api"')

        expected_error = ['Signature has expired.']
        self.assertEqual(response_content['errors'], expected_error)

    def test_post_invalid_token_failing_jwt_auth(self):
        """
        Ensure POSTing over JWT auth with invalid token fails
        """
        auth = 'Bearer abc123'
        response = self.client.post(
            '/jwt/',
            content_type='application/json',
            HTTP_AUTHORIZATION=auth
        )

        response_content = json.loads(smart_text(response.content))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'JWT realm="api"')

        expected_error = ['Error decoding signature.']
        self.assertEqual(response_content['errors'], expected_error)
