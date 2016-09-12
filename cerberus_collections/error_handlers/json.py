from io import IOBase
import json
from socket import socket

from cerberus import Validator
from cerberus.errors import BaseErrorHandler, ErrorList

from cerberus_collections.error_handlers.mixins import BufferAdapter, ValidationContext
from cerberus_collections.utils import error_as_dict, error_from_dict


def extract_mapping_from_json_chunk(s):
    """ Tries to extract a mapping from an arbitrary sized json chunk.

        :returns: A two-value tuple with the extracted mapping string or
                  :obj:`None` and remaining part of the chunk.
        :rtype: str
    """
    # cython candidate
    escaped = quoted = False
    ob = cb = 0

    for i, c in enumerate(s):
        if escaped:
            escaped = False
        elif c == '\\':
            escaped = True
        elif c == '"':
            quoted = not quoted
        elif c == '{' and not quoted:
            ob += 1
        elif c == '}' and not quoted:
            cb += 1
        if ob == cb:
            break
    else:
        return None, s

    return s[:i+1], s[i+2:].lstrip()


class JSONErrorHandler(BaseErrorHandler, BufferAdapter, ValidationContext):
    """ An error handler that (de-)serializes cerberus validation errors to and
        from JSON.

        Calling an instance without arguments returns the
        errors that were collected during the last validation of a
        :class:`~cerberus.Validator`, if the handler
        was bound to its :attr:`~cerberus.Validator.error_handler` property, as
        JSON string. That's what happens when you get the
        :attr:`~cerberus.Validator.errors` of a validator with this handler
        bound as its :attr:`~cerberus.Validator.error_handler`.

        If called with a sequence of :class:`~cerberus.errors.ValidationError`
        instances as argument, the returned JSON string represents these.

        During cerberus' validation it dumps json via a ``buffer`` object if
        provided.

        An instance is iterable and returns errors it reads from the ``buffer``
        object.

        All configuration options are accessible as instance properties.

        :param buffer: An object for I/O when emitting and iterating.
        :type buffer: :class:`io.IOBase` (like file objects),
                      :class:`socket.socket` or :obj:`None`
        :param compact: Omit unecessary whitespaces.
        :type compact: bool
        :param indent: Block indentation.
        :type indent: integer or :obj:`None`
        :param encoding: Character encoding.
        :type encoding: str
        :param consider_context: Write ``document_id`` and ``schema_id`` and check
                                 these while parsing.
        :type consider_context: bool
        :param document_id: An identifier that refers the document being validated.
        :type document_id: str
        :param schema_id: An identifier that refers the used validation schema.
        :type schema_id: str
        """
    def __init__(self, buffer=None, compact=True, indent=-1,
                 encoding='utf-8', consider_context=False,
                 document_id=None, schema_id=None):
        self.buffer = buffer
        self.compact = compact
        self.indent = indent
        self.encoding = encoding
        self.consider_context = consider_context
        self.document_id = document_id
        self.schema_id = schema_id
        self._cached_validation_signature = None

        self.errors = ErrorList()

    def __call__(self, errors=None):
        if isinstance(errors, Validator):
            errors = errors._errors
        elif errors is None:
            errors = self.errors

        errors = [error_as_dict(x) for x in errors]
        if self._validation_signature:
            for error in errors:
                error.update(self._validation_signature)
        return json.dumps(errors, **self._dump_kwargs)

    def __iter__(self):
        if self._buffer is None:
            raise RuntimeError("{} must have a 'buffer'-property set.".format(repr(self)))

        elif self._buffer_type is IOBase:
            self.__errors = json.load(self._buffer)
        elif self._buffer_type is socket:
            buffer = self._buffer.recv(1024).decode(self.encoding)
            if buffer.startswith('['):
                buffer = buffer[1:]
            self.__socketbuffer = buffer

        return self

    def __next__(self):
        return self._next_from_buffer()

    def __str__(self):
        return self()

    @property
    def _dump_kwargs(self):
        return {'indent': self.indent,
                'separators': (',', ':') if self.compact else None}

    def add(self, error):
        self.errors.append(error)

    def clear(self):
        """ Clears collected errors. """
        self.errors = ErrorList()

    def end(self, validator):
        if self._buffer_type is None:
            return

        self._write_to_buffer(self.__next_error_to_dump)

        self.used_emit_buffers[id(self._buffer)] -= 1
        if self.used_emit_buffers[id(self._buffer)]:
            self._write_to_buffer(',')
        else:
            self._write_to_buffer(']')
        self._cached_validation_signature = None

    def emit(self, error):
        if self._buffer_type is None:
            return

        if self.__next_error_to_dump:
            self._write_to_buffer(self.__next_error_to_dump + ',')

        error = error_as_dict(error)
        if self.consider_context:
            error.update(self._cached_validation_signature)
        self.__next_error_to_dump = json.dumps(error, **self._dump_kwargs)

    def extend(self, errors):
        self.errors.extend(errors)

    def _next_from_file(self):
        # TODO read file in chunks
        if self.__errors:
            error = self.__errors.pop()
            if self.consider_context:
                identifiers = self._pop_validation_signature(error)
                self._validate_signature(identifiers)
            return error_from_dict(error)
        else:
            raise StopIteration

    def _next_from_socket(self):
        buffer = self.__socketbuffer

        if buffer == ']':
            raise StopIteration

        while True:
            buffer += self._buffer.recv(1024).decode(self.encoding)
            if not buffer:
                error_string = None
                break

            error_string, buffer = extract_mapping_from_json_chunk(buffer)
            if error_string is not None:
                break

        if error_string is None:
            raise StopIteration

        self.__socketbuffer = buffer
        return error_from_dict(json.loads(error_string))

    def parse(self, _json, **parse_args):
        """ Parses JSON to cerberus error representations.

        :param _json: json-encoded error representation error or a list of these.
        :type _json: str
        :param document_id: Errors' ``document_id`` attributes must match
                            this one.
        :type document_id: str
        :param schema_id: Errors' ``schema_id`` attributes must match this
                          one.
        :type schema_id: str
        :param validate_signature: Controls whether to check validation
               signature.
        :type validate_signature: bool
        :returns: The parsed error or errors.
        :rtype: A :class:`~cerberus.errors.ValidationError` instance if an
                encoded mapping was provided, or a list of these in case
                of a list.
        """
        validate_signature = parse_args.pop('validate_signature',
                                            self.consider_context)

        if isinstance(_json, bytes):
            _json = _json.decode(self.encoding)
        _json = _json.strip()

        if _json.startswith('{'):
            error = json.loads(_json)
            if validate_signature:
                identifiers = self._pop_validation_signature(error)
                self._validate_signature(identifiers, **parse_args)
            return error_from_dict(error)
        elif _json.startswith('['):
            errors = json.loads(_json)
            if validate_signature:
                for error in errors:
                    identifiers = self._pop_validation_signature(error)
                    self._validate_signature(identifiers, **parse_args)
            return ErrorList(error_from_dict(x) for x in errors)
        else:
            raise RuntimeError

    def _pop_validation_signature(self, mapping):
        identifiers = {}
        identifiers['validator'] = mapping.pop('validator', None)
        identifiers['version'] = mapping.pop('version', None)
        identifiers['handler_version'] = mapping.pop('handler_version', None)
        identifiers['document_id'] = mapping.pop('document_id', None)
        identifiers['schema_id'] = mapping.pop('schema_id', None)
        return {k: v for k, v in identifiers.items() if v is not None}

    def read(self, buffer=None, **parse_args):
        """ Reads from a buffer and returns the parsed cerberus error
            representations.

            :param buffer: The buffer to read from, :attr:`~JSONErrorHandler.buffer`
                           is used if :obj:`None` is provided.
            :type buffer: :class:`io.IOBase` (like file objects) or
                          :class:`socket.socket`
            :param parse_args: See :meth:`~cerberus_collections.JSONErrorHandler.parse`'s
                                    keyword arguments.
            :returns: A list of :class:`~cerberus.errors.ValidationError`
                      instances.
        """
        buffer = buffer or self.buffer
        _parse_args = self._parse_args.copy()
        _parse_args.update(parse_args)

        if isinstance(buffer, IOBase):
            return self.parse(buffer.read(), **_parse_args)
        elif isinstance(buffer, socket):
            rcvd_buffer = b''
            while True:
                chunk = buffer.recv(1024)
                if not chunk:
                    break
                rcvd_buffer += chunk
            return self.parse(rcvd_buffer.decode(self.encoding), **_parse_args)

    def start(self, validator):
        if self._buffer_type is None:
            return

        if self.used_emit_buffers[id(self._buffer)] == 0:
            self._write_to_buffer('[')
        self.used_emit_buffers[id(self.buffer)] += 1
        self._cached_validation_signature = self._validation_signature.copy()
        self.__next_error_to_dump = ''
