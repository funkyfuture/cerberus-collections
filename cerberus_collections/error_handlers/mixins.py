from collections import defaultdict
from io import IOBase, BufferedIOBase, TextIOBase
from socket import socket
from warnings import warn

from cerberus import Validator

from cerberus_collections.error_handlers.exceptions import ValidationContextMismatch
from cerberus_collections.versions import CERBERUS_VERSION, __version__


class BufferAdapter:
    used_emit_buffers = defaultdict(int)

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, buffer):
        if isinstance(buffer, IOBase):
            self._buffer_type = IOBase
            if isinstance(buffer, BufferedIOBase):
                self._write_to_buffer = self._write_to_binary_file
            elif isinstance(buffer, TextIOBase):
                self._write_to_buffer = self._write_to_text_file
            self._next_from_buffer = self._next_from_file

        elif isinstance(buffer, socket):
            self._buffer_type = socket
            self._next_from_buffer = self._next_from_socket
            self._write_to_buffer = self._write_to_socket

        else:
            self._buffer_type = None
            self._next_from_buffer = self.__nop
            self._write_to_buffer = self.__nop
            if buffer is not None:
                warn('Unknown buffer type, errors will not be emitted withot '
                     'notice and the error handler is not iterable.')

        self._buffer = buffer

    def __nop(self, *args, **kwargs):
        pass

    def _next_from_file(self):
        raise NotImplementedError
    _next_from_socket = _next_from_file

    def _write_to_binary_file(self, data):
        if isinstance(data, str):
            data = data.encode(self.encoding)
        self._buffer.write(data)
        self._buffer.flush()

    def _write_to_text_file(self, data):
        if isinstance(data, bytes):
            data = data.decode(self.encoding)
        self._buffer.write(data)
        self._buffer.flush()

    def _write_to_socket(self, data):
        if not isinstance(data, bytes):
            data = data.encode(self.encoding)
        self._buffer.sendall(data)


class ValidationContext:
    @property
    def _parse_args(self):
        return {'document_id': self.document_id,
                'schema_id': self.schema_id,
                'validate_signature': self.consider_context}

    def _validate_signature(self, error_identifiers, document_id=None, schema_id=None):
        document_id = document_id or self.document_id
        schema_id = schema_id or self.schema_id

        schema = {'validator': {'allowed': ['cerberus']},
                  'version': {'allowed': [CERBERUS_VERSION]},
                  'handler_version': {'allowed': [__version__]}}
        if document_id is not None:
            schema.update({'document_id': {'allowed': [document_id]}})
        if schema_id is not None:
            schema.update({'schema_id': {'allowed': [schema_id]}})

        validator = Validator(schema, allow_unknown=True, ignore_none_values=True)
        validator(error_identifiers)

        det = validator.document_error_tree
        if det['validator'] or det['version']:
            warn('The parsed error/s was/were generated with a different validator: {} {} != {} {}'
                 .format('cerberus', CERBERUS_VERSION,
                         error_identifiers['validator'], error_identifiers['version']))
        if det['handler_version']:
            warn('The error/s was/were serialized with a different handler version: {} != {}'
                 .format(__version__, error_identifiers['handler_version']))
        if det['document_id']:
            raise ValidationContextMismatch("document_ids don't match: {} != {}"
                                            .format(document_id, error_identifiers['document_id']))
        if det['schema_id']:
            raise ValidationContextMismatch("schema_ids don't match: {} != {}"
                                            .format(schema_id, error_identifiers['schema_id']))

    @property
    def _validation_signature(self):
        if not self.consider_context:
            return {}
        result = {'validator': 'cerberus', 'version': CERBERUS_VERSION,
                  'handler_version': __version__}
        if self.document_id is not None:
            result['document_id'] = self.document_id
        if self.schema_id is not None:
            result['schema_id'] = self.schema_id
        return result
