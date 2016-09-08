# cerberus-collections

[Cerberus](http://python-cerberus.org) is a lightweight and extensible data
validation library for Python.

Here are the extensions.

## Contents

This package aims to provide various code pieces that add functionality for
validations.

Python 2 is not supposed to be supported, though some parts may run reliably.

### Error Handlers

- `cerberus_collections.XMLErrorHandler` (requires [lxml](https://pypi.org/project/lxml/))

([documentation](https://cerberus-collections.rtfd.io/en/latest/error_handlers.html))

##### TODO

- HumanReadable
- YAML
- json
- logger
- handler chainer

### Rules

### Types

##### TODO

- python builtin types https://github.com/nicolaiarocci/cerberus/issues/186
- common networking and posix data

### Validators

##### TODO

- PyObjectValidator


## Versioning scheme

The first version segment of a release matches the one of the Cerberus version 
it supports. The following parts reflect the release's month and possibly pre- 
or post-release segments.


## Contributing

If you have a Docker client installed, you can easily run all tests:

    <project_dir>/run-docker-tests


## TODO

- type annotations
- bump-script
- release-script
