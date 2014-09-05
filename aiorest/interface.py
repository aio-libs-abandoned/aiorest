import abc


# this is not needed as Resolver should be a target for customization
class AbstractServer(metaclass=abc.ABCMeta):
    # NOTE: AbstractServer is here only for generalization,
    #       to show an interface idea when building any other aiohttp-based
    #       server.

    @property
    @abc.abstractmethod
    def resolver(self):
        """Resolver instance."""

    # def add_url(self, *args, **kw):
    #     """Shortcut to resolver.add_url method."""
    #     # XXX: here only for backward compatibility. Add warning;
    #     return self.resolver.add_url(*args, **kw)

    @abc.abstractmethod
    def dispatch(self, request):
        """Dispatches request.

        Basically finds request handler using resolver,
        calls it (or yields from), dumps result to json string
        and returns it encoded to bytes.
        """

    @abc.abstractmethod
    def make_handler(self):
        """Callback to be used in asyncio.create_server call."""


class AbstractResolver(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def add_url(self, *args, **kw):
        """Registers URL."""

    @abc.abstractmethod
    def resolve(self, request):
        """Performs view callable lookup based on request.

        Returns handler to be used with request.
        """

    @abc.abstractmethod
    def url_for(self, *args, **kw):
        """Constructs url for specified arguments.

        Returns None if no url can not be found.
        May raise error if url can not be constructed with parameters supplied.

        If no reverse url resolving is needed this method
        should raise NotImplementedError.
        """


class RESTServer(AbstractServer):

    def __init__(self, resolver):
        self._resolver = resolver
        assert isinstance(resolver, AbstractResolver)

    def make_handler(self):

        class Handler:
            def handle_request(self, message, payload):
                pass

            def handle_error(self, *args, **kw):
                pass

        return Handler()

    @property
    def resolver(self):
        return self._resolver

    def dispatch(self, request):
        import aiohttp
        import asyncio
        from aiorest import errors
        import json
        handler = self.resolver.resolve(request)
        try:
            if asyncio.iscoroutinefunction(handler):
                ret = yield from handler(request)
            else:
                ret = handler(request)
        except errors.JsonDecodeError as exc:
            raise errors.RESTError(400, exc.reason)
        except errors.JsonLoadError as exc:
            raise errors.RESTError(400, exc.args[0])
        except aiohttp.HttpException as exc:
            raise
        except Exception as exc:
            raise aiohttp.HttpErrorException(
                500, "Internal Server Error") from exc
        else:
            return json.dumps(ret).encode('utf-8')

    def resolve(self, request):
        return self.resolver.resolve(request)
