class ErrorHandlerException(Exception):
    pass


class ContextMismatch(ErrorHandlerException):
    pass


class DecodingError(ErrorHandlerException):
    def __init__(self, _type, text):
        self.message = "Can't decode '{text}' to type '{type}'.".format(
            text=text, type=_type
        )
