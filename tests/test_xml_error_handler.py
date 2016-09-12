from io import BytesIO
from socket import socketpair
import sys

from cerberus.errors import ValidationError
from lxml.etree import _Element, tostring
from pytest import raises

from cerberus_collections import Validator, XMLErrorHandler
from cerberus_collections.error_handlers.exceptions import ValidationContextMismatch
from cerberus_collections.error_handlers.xml import Encoder, Decoder, DecodingError, element_from_error

from . import assert_equal_errors, sample_document, sample_schema


def test_encoder_decoder():
    x = Encoder.encode('a_string', 'foo')
    assert isinstance(x, _Element)
    assert x.attrib['type'] == 'str'
    assert x.text == 'foo'

    some_bytes = bytes([1, 2, 3])
    x = Encoder.encode('some_bytes', some_bytes)
    assert isinstance(x, _Element)
    assert x.attrib['type'] == 'bytes'
    assert x.text == 'AQID'
    assert Decoder.decode(x) == some_bytes


def test_decoding_error():
    x = Encoder.encode('a_bool', True)
    x.text = 'cat_in_a_box'
    with raises(DecodingError):
        Decoder.decode(x)

    x.attrib['type'] = 'boolean'
    with raises(NotImplementedError):
        Decoder.decode(x)


def write_errors_to_file(document_id, schema_id):
    buffer = BytesIO()
    validator = Validator(error_handler=(XMLErrorHandler,
                                         {'consider_context': True,
                                          'document_id': document_id,
                                          'schema_id': schema_id}))
    validator(sample_document, sample_schema)
    validator.errors.write(buffer)
    return buffer, validator


def read_errors_from_file(buffer, document_id, schema_id):
    buffer.seek(0)
    error_reader = XMLErrorHandler(document_id=document_id, schema_id=schema_id, consider_context=True)
    return error_reader.read(buffer)


def test_element():
    ve1 = ValidationError(('a_field',), ('a_field', 'type'), int('24', base=16), 'type', 'string', 0, ())
    ee = element_from_error(ve1, Encoder())
    assert ee.tag == 'error'
    assert ee.attrib['code'] == str(int('24', base=16))
    assert ee.attrib['rule'] == 'type'

    ve2 = XMLErrorHandler().parse(ee)
    assert ve1 == ve2


def test_simple():
    validator = Validator(error_handler=XMLErrorHandler)
    validator(sample_document, sample_schema)
    sys.stdout.write(tostring(validator.errors, encoding='unicode'))
    errors = str(validator.error_handler)
    parsed_errors = validator.error_handler.parse(errors)
    assert_equal_errors(validator._errors, parsed_errors)


def test_read_errors_from_file():
    buffer, validator = write_errors_to_file('foo', 'bar')
    parsed_errors = read_errors_from_file(buffer, 'foo', 'bar')
    assert_equal_errors(validator._errors, parsed_errors)

    with raises(ValidationContextMismatch):
        read_errors_from_file(buffer, 'bar', 'foo')


def test_write_and_read_socket():
    sender, receiver = socketpair()

    validator = Validator(sample_schema)
    validator(sample_document)
    handler = XMLErrorHandler()
    handler.extend(validator._errors)
    sender.sendall(str(handler).encode())
    sender.close()

    handler = XMLErrorHandler()
    parsed_errors = handler.read(receiver)
    receiver.close()

    assert_equal_errors(validator._errors, parsed_errors)


def test_iter_errors_from_file():
    buffer, validator = write_errors_to_file(None, None)
    buffer.seek(0)
    handler = XMLErrorHandler(buffer=buffer)
    parsed_errors = []
    for error in handler:
        parsed_errors.append(error)
    assert_equal_errors(validator._errors, parsed_errors)


def test_emit_and_iter_through_file():
    buffer = BytesIO()
    validator = Validator(sample_schema, error_handler=(XMLErrorHandler,
                                                        {'buffer': buffer,
                                                         'prettify': True}))
    validator(sample_document)

    buffer.seek(0)
    parsed_errors = [x for x in XMLErrorHandler(buffer=buffer)]
    assert_equal_errors(validator._errors, parsed_errors)


def test_emit_and_iter_through_socket():
    sender, receiver = socketpair()

    validator = Validator(sample_schema, error_handler=XMLErrorHandler(sender))
    validator(sample_document)
    sender.close()

    error_handler = XMLErrorHandler(receiver)
    received_errors = [x for x in error_handler]
    receiver.close()

    assert_equal_errors(validator._errors, received_errors)
