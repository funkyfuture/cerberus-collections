class ErrorHandlerException(Exception):
    """ Base class for all exceptions in this package. """
    pass


class DecodingError(ErrorHandlerException):
    """ Raised when a value representation can't be decoded. """
    def __init__(self, _type, text):
        self.message = "Can't decode '{text}' to type '{type}'.".format(
            text=text, type=_type
        )


class ValidationContextMismatch(ErrorHandlerException):
    """ Raised when context information provided by a serialized error
        representation doesn't match the expected from an error handler's
        configuration.
    """
    pass
