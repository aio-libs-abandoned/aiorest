import aiohttp
import asyncio
import json


class JsonLoadError(ValueError):
    pass


class JsonDecodeError(UnicodeDecodeError):
    pass


class RESTError(aiohttp.HttpProcessingError):
    """REST server error.

    Adds json_body to base aiohttp.HttpProcessingError
    """

    def __init__(self, code, message='', json_body={}, headers=None):
        super().__init__(code=code, message=message, headers=headers)
        if json_body is None:
            self.body = None
        else:
            body = {'error': json_body,
                    'error_reason': message,
                    'error_code': code}
            self.body = json.dumps(body).encode('utf-8')

    @asyncio.coroutine
    def write_response(self, response):
        if self.body is not None:
            response.add_headers(
                ('Content-Type', 'application/json; charset=utf-8'),
                ('Content-Length', str(len(self.body))),
                )
        else:
            response.add_headers(
                ('Content-Type', 'text/plain'),
                ('Content-Length', '0'),
                )
        if self.headers:
            response.add_headers(*self.headers)
        response.send_headers()

        if self.body is not None:
            response.write(self.body)
        yield from response.write_eof()


class HttpCorsOptions(RESTError):
    """Http exception to handle CORS preflight requests.

    Raised in RESTServer.dispatch.
    """

    def __init__(self, headers):
        super().__init__(200, json_body=None, headers=headers)
