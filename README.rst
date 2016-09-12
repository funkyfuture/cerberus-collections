cerberus-collections
====================

|latest| |python-support|

`Cerberus`_ is a lightweight and extensible data validation library for Python.

Here are the extensions.

Contents
++++++++

This package aims to provide various code pieces that add functionality for
validations.

Python 2 is not supposed to be supported, though some parts may run reliably.

Error Handlers
--------------

- :class:`~cerberus_collections.JSONErrorHandler`
- :class:`~cerberus_collections.XMLErrorHandler` (requires `lxml`_)

(`documentation <https://cerberus-collections.rtfd.io/en/latest/error_handlers.html>`_)

TODO
....

- HumanErrorhandler
- YAML
- logger
- handler chainer


Rules
-----


Types
-----

TODO
....

- python builtin types (https://github.com/nicolaiarocci/cerberus/issues/186)
- common networking and posix data

Validators
----------

TODO
....

- PyObjectValidator


Versioning scheme
+++++++++++++++++

The first version segment of a release matches the one of the Cerberus version
it supports. The following parts reflect the release's month and possibly pre-
or post-release segments.


Contributing
++++++++++++

If you have a Docker client installed, you can easily run all tests:

    <project_dir>/run-docker-tests


TODO
++++

- type annotations
- bump-script
- release-script
- maybe Cython


.. _`Cerberus`: http://python-cerberus.org
.. _`lxml`: https://pypi.python.org/pypi/lxml

.. |latest| image:: https://img.shields.io/pypi/v/cerberus-collections.svg
   :target: https://pypi.python.org/pypi/cerberus-collections
   :alt: Version
.. |python-support| image:: https://img.shields.io/pypi/pyversions/cerberus-collections.svg
   :target: https://pypi.python.org/pypi/cerberus-collections
   :alt: Python versions
