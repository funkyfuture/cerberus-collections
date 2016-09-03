__all__ = []

try:
    from cerberus_collections.error_handlers.xml import XMLErrorHandler
except ImportError:
    pass
else:
    __all__.append(XMLErrorHandler.__name__)
