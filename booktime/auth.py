from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token


class TokenGetAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        params = parse_qs(scope["query_string"])
        if b"token" in params:
            try:
                token_key = params[b"token"][0].decode()
                token = Token.objects.get(key=token_key)
                scope["user"] = token.user
            except Token.DoesNotExist:
                pass
        return self.inner(scope)


TokenGetAuthMiddlewareStack = lambda inner: TokenGetAuthMiddleware(
    AuthMiddlewareStack(inner)
)
