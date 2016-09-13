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

- ``cerberus_collections.JSONErrorHandler``
- ``cerberus_collections.XMLErrorHandler`` (requires `lxml`_)

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

If you wrote an extension for Cerberus that suites general use, you're welcome
to have it included here. If you're interested in one of the mentioned, yet
unimplemented units, your initiative is highly appreciated. As improvements of
documentation and tests are as well.

(`Issue tracker <https://github.com/funkyfuture/cerberus-collections/issues>`_)


If you have a Docker client installed, you can easily run tests against all
supported Python implementations and the documentation:

    <project_dir>/run-docker-tests


TODO
++++

- type annotations
- maybe Cython


.. _`Cerberus`: http://python-cerberus.org
.. _`lxml`: https://pypi.python.org/pypi/lxml

.. |latest| image:: https://img.shields.io/pypi/v/cerberus-collections.svg
   :target: https://pypi.python.org/pypi/cerberus-collections
   :alt: Version
.. |python-support| image:: https://img.shields.io/pypi/pyversions/cerberus-collections.svg
   :target: https://pypi.python.org/pypi/cerberus-collections
   :alt: Python versions
