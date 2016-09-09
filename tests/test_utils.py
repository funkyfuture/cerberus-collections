from cerberus_collections.utils import binary_to_base64, base64_to_bytes


def test_binary_encoding():
    x = bytes(b'1234')
    y = bytearray(x)
    assert binary_to_base64(x) == binary_to_base64(y)
    assert x == base64_to_bytes(binary_to_base64(y))
