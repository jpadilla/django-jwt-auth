from django.views.generic import View
from django.http import HttpResponse

from jwt_auth.compat import json
from jwt_auth.mixins import JSONWebTokenAuthMixin


class MockView(JSONWebTokenAuthMixin, View):
    def post(self, request):
        data = json.dumps({'username': request.user.username})
        return HttpResponse(data)
