sample_schema = {'a_dict': {'keyschema': {'type': 'integer'},
                            'valueschema': {'regex': '[a-z]*'}},
                 'a_list': {'schema': {'type': 'string',
                                       'oneof_regex': ['[a-z]*$', '[A-Z]*']}},
                 'fibonacci': {'allowed': [1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
                               'type': 'number',
                               'min': 0,
                               'max': 99,
                               'excludes': ['a_dict', 'a_list']}}
sample_document = {'a_dict': {0: 'abc', 'one': 'abc', 2: 'aBc', 'three': 'abC'},
                   'a_list': [0, 'abc', 'abC'],
                   'fibonacci': 42}


def assert_equal_errors(e1, e2):
    """ Tests whether the errors in e1 and e2 are identical. """
    e1.sort()
    e2.sort()
    assert len(e1) == len(e2)
    for e1, e2 in zip(e1, e2):
        assert e1 == e2
        assert e1.rule == e2.rule
        assert e1.constraint == e2.constraint
        assert e1.value == e2.value
        assert e1.info == e2.info
        if e1.is_group_error:
            assert_equal_errors(e1.child_errors, e2.child_errors)
