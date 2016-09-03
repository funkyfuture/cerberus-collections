#!/usr/bin/env python

from datetime import datetime
from os import path
import sys
import textwrap

collections_path = path.abspath(path.join(path.dirname(__file__), '..', '..', '..'))
sys.path.append(collections_path)
print(sys.path)
import cerberus_collections  # noqa: E402

schema = {'a_dict': {'keyschema': {'type': 'integer'},
                     'valueschema': {'regex': '[a-z]*'}},
          'a_list': {'schema': {'type': 'string',
                     'oneof_regex': ['[a-z]*', '[A-Z]*']}},
          'fibonacci': {'allowed': [1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
                        'type': 'number',
                        'min': 0,
                        'max': 99,
                        'excludes': ['a_dict', 'a_list']}}
document = {'a_dict': {0: 'abc', 'one': 'abc', 2: 'aBc', 'three': 'abC'},
            'a_list': [0, 'abc', 'abC'],
            'fibonacci': 42}

validator = cerberus_collections.Validator(schema)
validator(document)

# XML Error Handler

error_handler = \
    cerberus_collections.XMLErrorHandler(prettify=True, document_id='TARDIS',
                                         schema_id='HistMat', consider_context=True)
error_handler(validator._errors)
example = textwrap.indent(str(error_handler), '  ')
output_file = path.join(collections_path, 'docs', 'source', 'includes', 'xml_error_handler.rst')
with open(output_file, 'wt') as f:
    print('.. generated with version {} ({})\n'.format(cerberus_collections.__version__, datetime.now()), file=f)
    print('.. code-block:: xml\n\n' + example, file=f)
