"""Compatibility import; implementation lives in clients.pediatric_labels."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("parent_child_pharmacology.clients.pediatric_labels")
