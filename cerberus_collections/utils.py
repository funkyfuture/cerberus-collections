from base64 import b64encode, b64decode

from cerberus.errors import ErrorList, ValidationError


def binary_to_base64(value):
    if not isinstance(value, bytes):
        value = bytes(value)
    return b64encode(value).decode()


def base64_to_bytes(value):
    return b64decode(value)


def error_as_dict(error):
    mapping = {x: getattr(error, x) for x in ('code', 'constraint',
                                              'document_path', 'field', 'rule',
                                              'schema_path', 'value')}

    if error.is_group_error:
        child_errors = [error_as_dict(x) for x in error.child_errors]
        mapping['info'] = [child_errors] + list(error.info[1:])
    else:
        mapping['info'] = error.info

    return mapping


def error_from_dict(mapping):
    error = ValidationError(document_path=tuple(mapping['document_path']),
                            schema_path=tuple(mapping['schema_path']),
                            code=mapping['code'], rule=mapping['rule'],
                            constraint=mapping['constraint'], value=mapping['value'],
                            info=())

    if error.is_group_error:
        child_errors = ErrorList(error_from_dict(x) for x in mapping['info'][0])
        error.info = (child_errors,) + tuple(mapping['info'][1:])
    else:
        error.info = tuple(mapping['info'])

    return error
