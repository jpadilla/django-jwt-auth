import datetime

from django.conf import settings

from jwt_auth.utils import import_from_string


JWT_ENCODE_HANDLER = import_from_string(getattr(
    settings,
    'JWT_ENCODE_HANDLER',
    'jwt_auth.utils.jwt_encode_handler')
)

JWT_DECODE_HANDLER = import_from_string(getattr(
    settings,
    'JWT_DECODE_HANDLER',
    'jwt_auth.utils.jwt_decode_handler')
)

JWT_PAYLOAD_HANDLER = import_from_string(getattr(
    settings,
    'JWT_PAYLOAD_HANDLER',
    'jwt_auth.utils.jwt_payload_handler')
)

JWT_PAYLOAD_GET_USER_ID_HANDLER = import_from_string(getattr(
    settings,
    'JWT_PAYLOAD_GET_USER_ID_HANDLER',
    'jwt_auth.utils.jwt_get_user_id_from_payload_handler')
)

JWT_SECRET_KEY = getattr(
    settings,
    'JWT_SECRET_KEY',
    settings.SECRET_KEY
)

JWT_ALGORITHM = getattr(settings, 'JWT_ALGORITHM', 'HS256')

JWT_VERIFY = getattr(settings, 'JWT_VERIFY', True)

JWT_VERIFY_EXPIRATION = getattr(settings, 'JWT_VERIFY_EXPIRATION', True)

JWT_LEEWAY = getattr(settings, 'JWT_LEEWAY', 0)

JWT_EXPIRATION_DELTA = getattr(
    settings,
    'JWT_EXPIRATION_DELTA',
    datetime.timedelta(seconds=300)
)

JWT_ALLOW_REFRESH = getattr(settings, 'JWT_ALLOW_REFRESH', False)

JWT_REFRESH_EXPIRATION_DELTA = getattr(
    settings,
    'JWT_REFRESH_EXPIRATION_DELTA',
    datetime.timedelta(seconds=300)
)

JWT_AUTH_HEADER_PREFIX = getattr(settings, 'JWT_AUTH_HEADER_PREFIX', 'Bearer')
