"""Compatibility import; implementation lives in clients.lakehouse."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("parent_child_pharmacology.clients.lakehouse")
