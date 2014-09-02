# flake8: noqa

try:
    import json
except ImportError:
    from django.utils import simplejson as json

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text

try:
    # In 1.5 the test client uses force_bytes
    from django.utils.encoding import force_bytes as force_bytes_or_smart_bytes
except ImportError:
    # In 1.4 the test client just uses smart_str
    from django.utils.encoding import smart_str as force_bytes_or_smart_bytes
