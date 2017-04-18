from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in
from jwt_auth import settings


class JwtAuthAppConfig(AppConfig):
    name = 'jwt_auth'
    verbose_name = 'JwtAuth'

    def ready(self):
        super(JwtAuthAppConfig, self).ready()
        if settings.JWT_LOGIN_INTEGRATION:
            from . import signals

            user_logged_in.connect(
                signals.logged_in,
                dispatch_uid="user_logged_in")
