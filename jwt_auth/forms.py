from calendar import timegm
from datetime import datetime, timedelta

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist

from jwt_auth import settings
from jwt_auth.compat import User
from jwt_auth.utils import jwt_get_user_id_from_payload_handler


jwt_payload_handler = settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = settings.JWT_ENCODE_HANDLER
jwt_decode_handler = settings.JWT_DECODE_HANDLER
jwt_get_user_id_from_payload = settings.JWT_PAYLOAD_GET_USER_ID_HANDLER


class JSONWebTokenForm(forms.Form):
    password = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(JSONWebTokenForm, self).__init__(*args, **kwargs)

        # Dynamically add the USERNAME_FIELD to self.fields.
        self.fields[self.username_field] = forms.CharField()

    @property
    def username_field(self):
        try:
            return User.USERNAME_FIELD
        except AttributeError:
            return 'username'

    def clean(self):
        cleaned_data = super(JSONWebTokenForm, self).clean()
        credentials = {
            self.username_field: cleaned_data.get(self.username_field),
            'password': cleaned_data.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise forms.ValidationError(msg)

                payload = jwt_payload_handler(user)

                # Include original issued at time for a brand new token,
                # to allow token refresh
                if settings.JWT_ALLOW_REFRESH:
                    payload['orig_iat'] = timegm(
                        datetime.utcnow().utctimetuple()
                    )

                self.object = {
                    'token': jwt_encode_handler(payload)
                }
            else:
                msg = 'Unable to login with provided credentials.'
                raise forms.ValidationError(msg)
        else:
            msg = 'Must include "username" and "password"'
            raise forms.ValidationError(msg)


class JSONWebTokenRefreshForm(forms.Form):
    token = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(JSONWebTokenRefreshForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(JSONWebTokenRefreshForm, self).clean()

        old_payload = jwt_decode_handler(cleaned_data.get('token'))
        user_id = jwt_get_user_id_from_payload_handler(old_payload)

        # Verify user

        try:
            user = get_user_model().objects.get(id=user_id)
        except ObjectDoesNotExist:
            msg = 'Unable to login with provided credentials.'
            raise forms.ValidationError(msg)

        if not user.is_active:
            msg = 'User account is disabled.'
            raise forms.ValidationError(msg)

        # Verify orig_iat

        orig_iat = old_payload.get('orig_iat')
        if not orig_iat:
            msg = 'orig_iat was missing from payload.'
            raise forms.ValidationError(msg)

        # Verify expiration

        refresh_limit = settings.JWT_REFRESH_EXPIRATION_DELTA

        if isinstance(refresh_limit, timedelta):
            refresh_limit = (refresh_limit.days * 24 * 3600 +
                             refresh_limit.seconds)

        expiration_timestamp = orig_iat + int(refresh_limit)
        now_timestamp = timegm(datetime.utcnow().utctimetuple())

        if now_timestamp > expiration_timestamp:
            msg = 'Refresh has expired.'
            raise forms.ValidationError(msg)

        # Re-issue new token

        payload = jwt_payload_handler(user)

        # Include original issued at time for a brand new token,
        # to allow token refresh
        if settings.JWT_ALLOW_REFRESH:
            payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
            )

        self.object = {
            'token': jwt_encode_handler(payload)
        }
