from collections import Sequence, Mapping
from copy import deepcopy
from io import StringIO
from socket import socketpair
import sys

from pytest import raises

from cerberus_collections import Validator, JSONErrorHandler
from cerberus_collections.error_handlers.exceptions import ValidationContextMismatch

from . import assert_equal_errors, sample_document, sample_schema


def jsonify(obj):
    if isinstance(obj, Mapping):
        return {str(k): jsonify(v) for k, v in obj.items()}
    elif isinstance(obj, Sequence) and not isinstance(obj, str):
        return [jsonify(x) for x in obj]
    else:
        return obj


sample_schema = jsonify(deepcopy(sample_schema))
sample_document = jsonify(deepcopy(sample_document))


def write_errors_to_file(document_id, schema_id):
    buffer = StringIO()
    validator = Validator(error_handler=(JSONErrorHandler,
                                         {'consider_context': True,
                                          'document_id': document_id,
                                          'schema_id': schema_id}))
    validator(sample_document, sample_schema)
    buffer.write(validator.errors)
    return buffer, validator


def read_errors_from_file(buffer, document_id, schema_id):
    buffer.seek(0)
    print(buffer.read())
    buffer.seek(0)
    error_reader = JSONErrorHandler(
        document_id=document_id, schema_id=schema_id, consider_context=True)
    return error_reader.read(buffer)


def test_simple():
    validator = Validator(error_handler=JSONErrorHandler)
    validator(sample_document, sample_schema)
    sys.stdout.write(validator.errors)
    parsed_errors = validator.error_handler.parse(validator.errors)
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
    handler = JSONErrorHandler()
    handler.extend(validator._errors)
    sender.sendall(str(handler).encode())
    sender.close()

    handler = JSONErrorHandler()
    parsed_errors = handler.read(receiver)
    receiver.close()

    assert_equal_errors(validator._errors, parsed_errors)


def test_iter_errors_from_file():
    buffer, validator = write_errors_to_file(None, None)
    buffer.seek(0)
    handler = JSONErrorHandler(buffer=buffer)
    parsed_errors = []
    for error in handler:
        parsed_errors.append(error)
    assert_equal_errors(validator._errors, parsed_errors)


def test_emit_and_iter_through_file():
    buffer = StringIO()
    validator = Validator(sample_schema, error_handler=(JSONErrorHandler,
                                                        {'buffer': buffer,
                                                         'compact': False,
                                                         'indent': 2}))
    validator(sample_document)

    buffer.seek(0)
    print(buffer.read())
    buffer.seek(0)

    parsed_errors = [x for x in JSONErrorHandler(buffer=buffer)]
    assert_equal_errors(validator._errors, parsed_errors)


def test_emit_and_iter_through_socket():
    sender, receiver = socketpair()

    validator = Validator(sample_schema, error_handler=JSONErrorHandler(sender))
    validator(sample_document)
    sender.close()

    error_handler = JSONErrorHandler(receiver)
    received_errors = [x for x in error_handler]
    receiver.close()

    assert_equal_errors(validator._errors, received_errors)
