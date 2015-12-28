import pytest
from django.test import TestCase
from django.test.client import Client

from jwt_auth import utils
from jwt_auth.compat import json, User, smart_text


@pytest.mark.django_db
class ObtainJSONWebTokenTestCase(TestCase):
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

    def test_jwt_login_json(self):
        """
        Ensure JWT login view using JSON POST works.
        """
        response = self.client.post(
            '/auth-token/',
            json.dumps(self.data),
            content_type='application/json'
        )

        response_content = json.loads(smart_text(response.content))

        decoded_payload = utils.jwt_decode_handler(response_content['token'])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(decoded_payload['username'], self.username)

    def test_jwt_login_json_bad_creds(self):
        """
        Ensure JWT login view using JSON POST fails
        if bad credentials are used.
        """
        self.data['password'] = 'wrong'

        response = self.client.post(
            '/auth-token/',
            json.dumps(self.data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_jwt_login_json_missing_fields(self):
        """
        Ensure JWT login view using JSON POST fails if missing fields.
        """
        response = self.client.post(
            '/auth-token/',
            json.dumps({'username': self.username}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_jwt_login_with_expired_token(self):
        """
        Ensure JWT login view works even if expired token is provided
        """
        payload = utils.jwt_payload_handler(self.user)
        payload['exp'] = 1
        token = utils.jwt_encode_handler(payload)

        auth = 'Bearer {0}'.format(token)

        response = self.client.post(
            '/auth-token/',
            json.dumps(self.data),
            content_type='application/json',
            HTTP_AUTHORIZATION=auth
        )

        response_content = json.loads(smart_text(response.content))

        decoded_payload = utils.jwt_decode_handler(response_content['token'])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(decoded_payload['username'], self.username)
