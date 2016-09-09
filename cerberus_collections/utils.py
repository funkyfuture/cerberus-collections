from base64 import b64encode, b64decode


def binary_to_base64(value):
    if not isinstance(value, bytes):
        value = bytes(value)
    return b64encode(value).decode()


def base64_to_bytes(value):
    return b64decode(value)
