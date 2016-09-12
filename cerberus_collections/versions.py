import cerberus

CERBERUS_VERSION = cerberus.__version__
COLLECTIONS_RELEASE = '2016.09-a1'
__version__ = CERBERUS_VERSION.split('.', 1)[0] + '.' + COLLECTIONS_RELEASE
