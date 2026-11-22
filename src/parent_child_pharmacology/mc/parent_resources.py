"""Compatibility import; implementation lives in clients.parent_resources."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("parent_child_pharmacology.clients.parent_resources")
