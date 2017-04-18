"""
Signal handlers for jwt_auth app
"""
from calendar import timegm
from datetime import datetime

from jwt_auth import settings


jwt_payload_handler = settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = settings.JWT_ENCODE_HANDLER


def logged_in(sender, request, user, **kwargs):
    """
    Put JWT token in session
    """

    payload = jwt_payload_handler(user)

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    request.session['jwt_token'] = jwt_encode_handler(payload)
