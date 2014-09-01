from django.conf.urls import patterns

from jwt_auth.views import ObtainJSONWebToken

from tests.views import MockView


urlpatterns = patterns(
    '',
    (r'^jwt/$', MockView.as_view()),
    (r'^auth-token/$', ObtainJSONWebToken.as_view()),
)
