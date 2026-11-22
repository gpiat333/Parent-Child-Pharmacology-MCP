"""Compatibility import; implementation lives in models.contracts."""
import sys
from importlib import import_module
sys.modules[__name__] = import_module('models.contracts')
