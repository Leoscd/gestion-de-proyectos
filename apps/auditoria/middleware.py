from contextvars import ContextVar

_request_actual = ContextVar("request_actual", default=None)


def request_actual():
    return _request_actual.get()


class RequestActualMiddleware:
    """Guarda el request en curso para que `registrar()` sepa quién y desde qué IP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = _request_actual.set(request)
        try:
            return self.get_response(request)
        finally:
            _request_actual.reset(token)
