Error Handlers
==============

Error handlers are used to handle the errors issued by a :class:`~cerberus.Validator`
like serialising them.

JSON
----

The :class:`JSONErrorHandler` can be used to store error information as JSON:

.. testcode::

   validator = Validator(error_handler=cerberus_collections.JSONErrorHandler)
   validator(document, schema)
   with open('errors.json', 'wt') as f:
      f.write(validator.errors)

Or communicate errors to another instance via a socket:

.. testcode::

   from socket import socketpair
   sender, receiver = socketpair()

   validator = Validator(error_handler=(cerberus_collections.JSONErrorHandler,
                                        {'buffer': sender}))
   validator(document, schema)
   sender.close()

   handler = cerberus_collections.JSONErrorHandler(receiver)
   received_errors = [x for x in handler]
   receiver.close()

.. admonition:: warning

   Keep in my that JSON only supports few types, you should thus only use
   these in documents and schemas. Dictionary keys should only be strings.

API
...

.. autoclass:: cerberus_collections.JSONErrorHandler
   :members: clear, parse, read

Example dump
............

.. todo:: collapes

.. include:: includes/json_error_handler.rst


XML
---

The :class:`XMLErrorHandler` can be used to store error information as XML:

.. testcode::

   validator = Validator(error_handler=cerberus_collections.XMLErrorHandler)
   validator(document, schema)
   with open('errors.xml', 'wb') as f:
      validator.errors.write(f)

Or communicate errors to another instance via a socket:

.. testcode::

   from socket import socketpair
   sender, receiver = socketpair()

   validator = Validator(error_handler=(cerberus_collections.XMLErrorHandler,
                                        {'buffer': sender}))
   validator(document, schema)
   sender.close()

   handler = cerberus_collections.XMLErrorHandler(receiver)
   received_errors = [x for x in handler]
   receiver.close()

The default encoder and decoder support all of Python's builtin types except
``range`` and ``memoryview``.

.. admonition::  Requirements

   `lxml <http://lxml.de>`_ (`PyPI <https://pypi.python.org/pypi/lxml/>`_)

API
...

.. autoclass:: cerberus_collections.XMLErrorHandler
   :members: clear, parse, read

.. autoclass:: cerberus_collections.error_handlers.xml.Encoder
   :members: encode

.. autoclass:: cerberus_collections.error_handlers.xml.Decoder
   :members: decode

Example dump
............

.. todo:: collapes

.. include:: includes/xml_error_handler.rst


Exceptions
----------

.. automodule:: cerberus_collections.error_handlers.exceptions
   :members:
