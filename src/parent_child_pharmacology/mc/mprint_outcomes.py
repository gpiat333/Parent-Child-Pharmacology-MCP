"""Compatibility import; implementation lives in clients.mprint_outcomes."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("parent_child_pharmacology.clients.mprint_outcomes")
