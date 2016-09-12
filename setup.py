#!/usr/bin/env python

import sys
from setuptools import setup


if sys.version_info < (3, 4):
    raise SystemExit('Requires Python 3.4 or newer.')


requirements = [x for x in open('requirements.txt').readlines() if x]
for x in requirements:
    if x.startswith('cerberus~='):
        CERBERUS_VERSION = x.split('~=')[1].strip()
        break

setup(
    name='cerberus-collections',
    version=CERBERUS_VERSION.split('.', 1)[0] + '.2016.09-a1',
    packages=['cerberus_collections'],
    url='https://github.com/funkyfuture/cerberus-collections',
    license='ISC',
    platforms=["any"],
    author='Frank Sachsenheim',
    author_email='funkyfuture@riseup.net',
    description='Extensions for cerberus, a lightweight and extensible data validation library for Python',
    long_description=open('README.rst').read(),
    install_requires=requirements,
    keywords=['validation', 'schema', 'xml'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
