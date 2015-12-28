from __future__ import unicode_literals
from datetime import datetime
import importlib

import jwt


def jwt_payload_handler(user):
    from jwt_auth import settings

    try:
        username = user.get_username()
    except AttributeError:
        username = user.username

    return {
        'user_id': user.pk,
        'email': user.email,
        'username': username,
        'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
    }


def jwt_get_user_id_from_payload_handler(payload):
    """
    Override this function if user_id is formatted differently in payload
    """
    user_id = payload.get('user_id')
    return user_id


def jwt_encode_handler(payload):
    from jwt_auth import settings

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    ).decode('utf-8')


def jwt_decode_handler(token):
    from jwt_auth import settings

    options = {
        'verify_exp': settings.JWT_VERIFY_EXPIRATION,
    }

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        settings.JWT_VERIFY,
        options=options,
        leeway=settings.JWT_LEEWAY
    )


def import_from_string(val):
    """
    Attempt to import a class from a string representation.

    From: https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/settings.py
    """
    try:
        # Nod to tastypie's use of importlib.
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for setting. %s: %s." % (val, e.__class__.__name__, e)
        raise ImportError(msg)


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.
    From: https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/authentication.py
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')

    if isinstance(auth, type('')):
        # Work around django test client oddness
        auth = auth.encode('iso-8859-1')

    return auth
