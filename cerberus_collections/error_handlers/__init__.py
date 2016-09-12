__all__ = []

from cerberus_collections.error_handlers.json import JSONErrorHandler  # noqa: E402
__all__.append(JSONErrorHandler.__name__)

try:
    from cerberus_collections.error_handlers.xml import XMLErrorHandler
except ImportError:
    pass
else:
    __all__.append(XMLErrorHandler.__name__)
