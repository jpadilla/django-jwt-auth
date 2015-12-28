from django.http import HttpResponse

import jwt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from jwt_auth import settings, exceptions
from jwt_auth.utils import get_authorization_header
from jwt_auth.compat import json, smart_text, User


jwt_decode_handler = settings.JWT_DECODE_HANDLER
jwt_get_user_id_from_payload = settings.JWT_PAYLOAD_GET_USER_ID_HANDLER


class JSONWebTokenAuthMixin(object):
    """
    Token based authentication using the JSON Web Token standard.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        try:
            request.user, request.token = self.authenticate(request)
        except exceptions.AuthenticationFailed as e:
            response = HttpResponse(
                json.dumps({'errors': [str(e)]}),
                status=401,
                content_type='application/json'
            )

            response['WWW-Authenticate'] = self.authenticate_header(request)

            return response

        return super(JSONWebTokenAuthMixin, self).dispatch(
            request, *args, **kwargs)

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
            raise exceptions.AuthenticationFailed()

        if len(auth) == 1:
            msg = 'Invalid Authorization header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = ('Invalid Authorization header. Credentials string '
                   'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            payload = jwt_decode_handler(auth[1])
        except jwt.ExpiredSignature:
            msg = 'Signature has expired.'
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = 'Error decoding signature.'
            raise exceptions.AuthenticationFailed(msg)

        user = self.authenticate_credentials(payload)

        return (user, auth[1])

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        try:
            user_id = jwt_get_user_id_from_payload(payload)

            if user_id:
                user = User.objects.get(pk=user_id, is_active=True)
            else:
                msg = 'Invalid payload'
                raise exceptions.AuthenticationFailed(msg)
        except User.DoesNotExist:
            msg = 'Invalid signature'
            raise exceptions.AuthenticationFailed(msg)

        return user

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'JWT realm="{0}"'.format(self.www_authenticate_realm)
