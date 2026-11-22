"""Compatibility import; implementation lives in core.http."""
import sys
from importlib import import_module
sys.modules[__name__] = import_module('core.http')
