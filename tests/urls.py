from django.conf.urls import patterns

from tests.views import MockView


urlpatterns = patterns(
    '',
    (r'^jwt/$', MockView.as_view()),
    (r'^auth-token/$', 'jwt_auth.views.obtain_jwt_token'),
)
