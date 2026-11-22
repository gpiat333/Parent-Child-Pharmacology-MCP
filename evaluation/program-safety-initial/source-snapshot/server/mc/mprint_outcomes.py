"""Compatibility import; implementation lives in clients.mprint_outcomes."""
import sys
from importlib import import_module
sys.modules[__name__] = import_module('clients.mprint_outcomes')
