# cerberus-collections

Extensions for [cerberus](http://python-cerberus.org), a lightweight and extensible data validation library for Python.

## Contents

### Error Handlers

- `cerberus_collections.XMLErrorHandler` (requires [lxml](https://pypi.org/project/lxml/))

([documentation](docs/source/error_handlers.rst))

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
