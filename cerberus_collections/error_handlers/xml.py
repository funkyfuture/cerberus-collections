from collections import Sequence
from datetime import datetime
from io import IOBase
from socket import socket
from warnings import warn

from lxml.etree import Element, ElementTree, _ElementTree, iterparse
from lxml.etree import tostring as element_to_string
from lxml.etree import fromstring as element_from_string

from cerberus import Validator
from cerberus.errors import BaseErrorHandler, ValidationError

from cerberus_collections.error_handlers.exceptions import DecodingError
from cerberus_collections.error_handlers.mixins import BufferAdapter, ValidationContext
from cerberus_collections.utils import binary_to_base64, base64_to_bytes


class Encoder:
    """ Encode Python objects to XML elements.

        Supports almost all builtin types. If ``value`` has no complementing
        method ``_encode_<type name>`` here, its string representation will be
        used.

        Instances are callable as proxy to :meth:`Encoder.encode`.
    """
    @classmethod
    def encode(cls, tag, value):
        """ Generate an xml representation of a given value.

            :param tag: The tag of the resulting element, usually a variable
                        name or descriptor.
            :type tag: :class:`str`
            :param value: The value to encode.
            :type value: any :class:`object`
            :rtype: :class:`lxml._Element`
        """
        value_type = type(value).__name__
        encoder = getattr(cls, '_encode_' + value_type, None)
        element = Element(tag, type=value_type)
        if encoder is None:
            element.text = str(value)
        else:
            encoded_value = encoder(value)
            if isinstance(encoded_value, str):
                element.text = encoded_value
            elif isinstance(encoded_value, Sequence):
                element.extend(encoded_value)
            else:
                raise RuntimeError
        return element

    def __call__(self, *args, **kwargs):
        return self.encode(*args, **kwargs)

    @staticmethod
    def _encode_bytes(value):
        return binary_to_base64(value)

    @staticmethod
    def _encode_bytearray(value):
        return binary_to_base64(bytes(value))

    @classmethod
    def _ncd_mapping(cls, mapping):
        result = []
        for key in mapping:
            x = Element('item')
            x.extend((cls.encode('key', key),
                      cls.encode('value', mapping[key])))
            result.append(x)
        return result

    _encode_dict = _ncd_mapping

    @classmethod
    def _ncd_sequence(cls, sequence):
        return [cls.encode('item', x) for x in sequence]

    _encode_list = _encode_set = _encode_frozenset = _encode_tuple = \
        _ncd_sequence


class Decoder:
    """ Decode XML elements to Python objects.

        Supports almost all builtin types as well as :class:`datetime.date`
        and :class:`datetime.datetime`.

        Instances are callable as proxy to :meth:`Decoder.decode`.
    """
    @classmethod
    def decode(cls, element):
        """ Decodes an xml representation according to the elements's type
            attribute to a Python object.

            :param element: The XML representation to decode, must have a
                            ``type``-attribute that is used to lookup the
                            decoding method ``_decode_<type name>``.
            :type element: :class:`lxml._Element`
            :returns: The decoded object.
        """
        value_type = element.attrib['type']
        decoder = getattr(cls, '_decode_' + value_type, None)
        if decoder is None:
            raise NotImplementedError('No decoder for {} found.'.format(value_type))
        else:
            try:
                return decoder(element)
            except (AssertionError, ValueError):
                raise DecodingError(value_type, element.text)

    def __call__(self, *args, **kwargs):
        return self.decode(*args, **kwargs)

    @staticmethod
    def _decode_bool(element):
        if element.text == 'True':
            return True
        elif element.text == 'False':
            return False
        else:
            raise ValueError

    @staticmethod
    def _decode_bytes(element):
        return base64_to_bytes(element.text)

    @staticmethod
    def _decode_bytearray(element):
        return bytearray(base64_to_bytes(element.text))

    @staticmethod
    def _decode_complex(element):
        real, imag = map(int, element.text[1:-2].split('+'))
        return complex(real, imag)

    @staticmethod
    def _decode_date(element):
        return datetime.strptime(element.text, '%Y-%m-%d').date()

    @staticmethod
    def _decode_datetime(element):
        return datetime.strptime(element.text, '%Y-%m-%d %H:%M:%S.%f')

    @classmethod
    def _decode_dict(cls, element):
        result = {}
        for item in element.iterfind('item'):
            key = cls.decode(item.find('key'))
            value = cls.decode(item.find('value'))
            result[key] = value
        return result

    @staticmethod
    def _decode_float(element):
        return float(element.text)

    @classmethod
    def _decode_frozenset(cls, element):
        return frozenset(cls._decode_list(element))

    @staticmethod
    def _decode_int(element):
        return int(element.text)

    @classmethod
    def _decode_list(cls, element):
        return [cls.decode(x) for x in element.iterfind('item')]

    @classmethod
    def _decode_set(cls, element):
        return set(cls._decode_list(element))

    @staticmethod
    def _decode_str(element):
        return element.text

    @classmethod
    def _decode_tuple(cls, element):
        return tuple(cls._decode_list(element))


default_encoder, default_decoder = Encoder(), Decoder()


def element_from_error(error, encoder):
    """ Makes an XML element representing a validation error.

        :param error: The error to encode.
        :type error: :class:`~cerberus.errors.ValidationError`
        :param encoder: An encoder instance.
        :type encoder: Something alike :class:`Encoder`.
        :returns: An XML representation of the given error including childerrors.
        :rtype: :class:`lxml._Element`
    """
    element = Element('error', attrib={
        'id': hex(hash(error))[3:],
        'code': str(error.code),
        'rule': error.rule or 'None'
    })

    for error_attribute in ('document_path', 'schema_path', 'constraint', 'value'):
        value = getattr(error, error_attribute, None)
        if value is not None:
            element.append(encoder(error_attribute, value))

    if error.is_logic_error:
        element.attrib['definitions'] = str(error.info[2])
        element.attrib['validated'] = str(error.info[1])
        for definition in error.definitions_errors:
            for child_error in error.definitions_errors[definition]:
                child_element = element_from_error(child_error, encoder)
                child_element.attrib['definition'] = str(definition)
                element.append(child_element)

    elif error.is_group_error:
        element.extend([element_from_error(x, encoder) for x in error.child_errors])

    else:
        element.extend([encoder('info', x) for x in error.info])

    return element


def error_from_element(element, decoder):
    """ Transforms an XML error representation to a validation error object.

        :param error: The XML element to transform.
        :type error: :class:`lxml._Element`
        :param decoder: An decoder instance.
        :type decoder: Something alike :class:`Decoder`.
        :returns: A validation error object.
        :rtype: :class:`~cerberus.errors.ValidationError`
    """
    rule = None if element.attrib['rule'] == 'None' else element.attrib['rule']
    constraint = element.find('constraint')
    if constraint is not None:
        constraint = decoder(constraint)

    error = ValidationError(decoder(element.find('document_path')),
                            decoder(element.find('schema_path')),
                            int(element.attrib['code']), rule, constraint,
                            decoder(element.find('value')),
                            info=())

    if error.is_group_error:
        error.info = ([error_from_element(x, decoder) for x in element.iterfind('error')],)
        if error.is_logic_error:
            error.info += (int(element.attrib['validated']), int(element.attrib['definitions']))
    else:
        error.info = tuple((decoder(x) for x in element.iterfind('info')))

    return error


class XMLErrorHandler(BaseErrorHandler, BufferAdapter, ValidationContext):
    """ An error handler that (de-)serializes cerberus validation errors to and
        from XML.

        Calling an instance without arguments returns the
        errors that were collected during the last validation of a
        :class:`~cerberus.Validator`, if the handler
        was bound to its :attr:`~cerberus.Validator.error_handler` property, as
        :class:`~lxml._ElementTree`. That's what happens when you
        get the :attr:`~cerberus.Validator.errors` of a validator with this
        handler bound as its :attr:`~cerberus.Validator.error_handler`.

        If called with a sequence of :class:`~cerberus.errors.ValidationError`
        instances as argument, the returned tree represents these.

        During cerberus' validation it dumps xml via a ``buffer`` object if
        provided.

        An instance is iterable and returns errors it reads from the ``buffer``
        object.

        All configuration options are accessible as instance properties.

        :param buffer: An object for I/O when emitting and iterating.
        :type buffer: :class:`io.IOBase` (like file objects),
                      :class:`socket.socket` or :obj:`None`
        :param prettify: Prettify rendered xml.
        :type prettify: bool
        :param encoding: Character encoding.
        :type encoding: str
        :param consider_context: Write ``document_id`` and ``schema_id`` and check
                                 these while parsing.
        :type consider_context: bool
        :param document_id: An identifier that refers the document being validated.
        :type document_id: str
        :param schema_id: An identifier that refers the used validation schema.
        :type schema_id: str
        :param encoder: An instance of something alike
                        :class:`~cerberus_collections.error_handlers.xml.Encoder`.
        :param decoder: An instance of something alike
                        :class:`~cerberus_collections.error_handlers.xml.Decoder`.
    """
    encoder = default_encoder
    decoder = default_decoder

    # TODO add compress option
    def __init__(self, buffer=None, prettify=False, encoding='utf-8',
                 consider_context=False, document_id=None, schema_id=None,
                 encoder=None, decoder=None):
        self.buffer = buffer
        self.prettify = prettify
        self.encoding = encoding
        self.consider_context = consider_context
        self.document_id = document_id
        self.schema_id = schema_id
        self._cached_validation_signature = None
        if encoder:
            self.encoder = encoder
        if decoder:
            self.decoder = decoder

        self.clear()

    def __call__(self, errors=None):
        if isinstance(errors, Validator):
            errors = errors._errors
        if errors is not None:
            self.clear()
            self.root.extend([element_from_error(x, self.encoder) for x in errors])
        return self.tree

    def __iter__(self):
        if self._buffer is None:
            raise RuntimeError("{} must have a 'buffer'-property set.".format(repr(self)))

        elif self._buffer_type is IOBase:
            self.__iterparser = iterparse(self._buffer, events=('start', 'end'))

        elif self._buffer_type is socket:
            buffer = b''
            while b'>' not in buffer:
                buffer += self._buffer.recv(1024)

            if buffer.startswith(b'<errors'):
                container_element, self.__socketbuffer = buffer.split(b'>', 1)
                container_element += b'></errors>'
                container_element = element_from_string(container_element)
                self._validate_signature(container_element)
            else:
                warn('Opening <errors> element is missing.')
                if not buffer.startswith(b'<error'):
                    raise StopIteration

        return self

    def __next__(self):
        return self._next_from_buffer()

    def __str__(self):
        return self._as_string(self.root).decode(self.encoding)

    def add(self, error):
        self.root.append(element_from_error(error, self.encoder))

    def _as_string(self, element):
        return element_to_string(element, encoding=self.encoding,
                                 xml_declaration=False, pretty_print=self.prettify)

    def clear(self):
        """ Clears collected errors. """
        self.root = Element('errors', attrib=self._validation_signature)
        self.tree = ElementTree(self.root)

    def end(self, validator):
        if self._buffer_type is None:
            return

        self.used_emit_buffers[id(self._buffer)] -= 1
        if not self.used_emit_buffers[id(self._buffer)]:
            self._write_to_buffer('</errors>')
        self._cached_validation_signature = None

    def emit(self, error):
        if self._buffer_type is None:
            return
        result = element_from_error(error, self.encoder)
        result.attrib.update(self._cached_validation_signature)
        result = self._as_string(result)

        self._write_to_buffer(result.strip())

    def _next_from_file(self):
        depth = 0
        while True:
            event, element = next(self.__iterparser)
            if element.tag != 'error':
                continue
            if event == 'start':
                depth += 1
            elif event == 'end':
                depth -= 1
                if depth == 0:
                    return self.parse(element, **self._parse_args)

    def _next_from_socket(self):
        element_string = b''
        buffer = self.__socketbuffer

        if buffer == b'</errors>':
            raise StopIteration

        while True:
            if b'</error>' not in buffer:
                buffer += self._buffer.recv(1024)
                continue

            element_part, buffer = buffer.split(b'</error>', 1)
            element_string += (element_part + b'</error>')
            while buffer.startswith(b'</error>'):
                element_string += b'</error>'
                buffer = buffer[len(b'</error>'):]

            if element_string.count(b'<error') > element_string.count(b'</error>'):
                continue

            self.__socketbuffer = buffer
            return self.parse(element_string, **self._parse_args)

    def parse(self, _input, document_id=None, schema_id=None, validate_signature=True):
        """ Parses XML, represented in different forms, to cerberus error
            representations.

            :param _input: The XML to parse.
            :type _input: bytes, str, :class:`lxml._Element` or
                          :class:`lxml._ElementTree` instances.
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
                    ``error``-element was provided, or a list of these in case
                    of an ``errors``-element.
        """
        if isinstance(_input, bytes):
            _input = _input.decode(self.encoding)
        if isinstance(_input, str):
            _input = element_from_string(_input)
        if isinstance(_input, _ElementTree):
            _input = _input.getroot()

        if validate_signature:
            self._validate_signature(_input, document_id, schema_id)

        if _input.tag == 'errors':
            return [self.parse(x, validate_signature=False) for x in _input.iterfind('error')]
        elif _input.tag == 'error':
            return error_from_element(_input, self.decoder)

    def read(self, buffer=None, **parse_args):
        """ Reads from a buffer and returns the parsed cerberus error
            representations.

            :param buffer: The buffer to read from, :attr:`buffer` is used if
                           :obj:`None` is provided.
            :type buffer: :class:`io.IOBase` (like file objects) or
                          :class:`socket.socket`
            :param parse_args: See :meth:`~cerberus_collections.XMLErrorHandler.parse`'s
                                    keyword arguments.
            :returns: A list of :class:`~cerberus.errors.ValidationError`
                      instances.
        """
        buffer = buffer or self._buffer
        _parse_args = self._parse_args.copy()
        _parse_args.update(parse_args)

        if isinstance(buffer, IOBase):
            return self.parse(ElementTree().parse(buffer), **_parse_args)
        elif isinstance(buffer, socket):
            recv_buffer = b''
            while True:
                chunk = buffer.recv(4096)
                if not chunk:
                    break
                recv_buffer += chunk
            return self.parse(element_from_string(recv_buffer), **_parse_args)
        else:
            raise RuntimeError("Can't read from object %s" % repr(buffer))

    def start(self, validator):
        if self._buffer_type is None:
            return

        self._cached_validation_signature = self._validation_signature
        if id(self._buffer) not in self.used_emit_buffers:
            container_element = Element('errors', self._validation_signature)
            container_element = element_to_string(container_element, method='html')
            self._write_to_buffer(container_element[:-len('</errors>')])
        self.used_emit_buffers[id(self._buffer)] += 1

    def _validate_signature(self, element, *args, **kwargs):
        super()._validate_signature(dict(element.attrib), *args, **kwargs)
