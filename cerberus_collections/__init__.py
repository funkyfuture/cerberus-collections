import cerberus
from cerberus.utils import validator_factory  # noqa: F401

from cerberus_collections.error_handlers import *  # noqa: F401, F403
from cerberus_collections.versions import __version__  # noqa: F401

VanillaValidator = Validator = cerberus.Validator
