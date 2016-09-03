import sys

if sys.version_info < (3, 5):
    import binascii

    def binary_to_hexstring(value):
        return binascii.hexlify(value).decode('utf-8')

    def hexstring_to_bytes(value):
        return binascii.unhexlify(value)
else:
    def binary_to_hexstring(value):
        return value.hex()

    def hexstring_to_bytes(value):
        return bytes.fromhex(value)
