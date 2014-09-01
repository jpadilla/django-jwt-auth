class AuthenticationFailed(Exception):
    status_code = 401
    detail = 'Incorrect authentication credentials.'

    def __init__(self, detail=None):
        self.detail = detail or self.detail

    def __str__(self):
        return self.detail
