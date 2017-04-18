import jwt
from jwt_auth import settings, exceptions
from jwt_auth.utils import get_authorization_header
from jwt_auth.compat import json, smart_text, User

import logging
logger = logging.getLogger(__name__)

jwt_decode_handler = settings.JWT_DECODE_HANDLER
jwt_get_user_id_from_payload = settings.JWT_PAYLOAD_GET_USER_ID_HANDLER


class JWTAuthenticationMiddleware(object):
    """
    Token based authentication using the JSON Web Token standard.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_request(self, request):
        try:
            auth = get_authorization_header(request).split()
            auth_header_prefix = settings.JWT_AUTH_HEADER_PREFIX.lower()

            if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
                raise exceptions.AuthenticationFailed()

            if len(auth) == 1:
                msg = 'Invalid Authorization header. No credentials provided.'
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = ('Invalid Authorization header. Credentials string should not contain spaces.')
                raise exceptions.AuthenticationFailed(msg)

            try:
                payload = jwt_decode_handler(auth[1])
            except jwt.ExpiredSignature:
                msg = 'Signature has expired.'
                raise exceptions.AuthenticationFailed(msg)
            except jwt.DecodeError:
                msg = 'Error decoding signature.'
                raise exceptions.AuthenticationFailed(msg)

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

            request.user = user
        except exceptions.AuthenticationFailed as e:
            logger.exception(e)

    def process_response(self, request, response):
        return response
