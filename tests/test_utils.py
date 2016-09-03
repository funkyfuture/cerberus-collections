from cerberus_collections.utils import binary_to_hexstring, hexstring_to_bytes


def test_binary_encoding():
    x = bytes(b'1234')
    y = bytearray(x)
    assert binary_to_hexstring(x) == binary_to_hexstring(y)
    assert x == hexstring_to_bytes(binary_to_hexstring(y))
