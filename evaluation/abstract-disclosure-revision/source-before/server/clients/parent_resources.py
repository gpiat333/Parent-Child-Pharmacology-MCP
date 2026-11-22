"""Compatibility exports for source-specific navigation adapters."""
import sys
from types import ModuleType
from importlib import import_module
_MODULES = [import_module('clients.'+name) for name in ['parent_common', 'fda_navigation', 'trial_navigation', 'parent_evidence', 'federal_register']]
for _module in _MODULES:
    for _name, _value in vars(_module).items():
        if not _name.startswith('__') and _name not in globals(): globals()[_name]=_value
class _Facade(ModuleType):
    def __setattr__(self,name,value):
        for module in _MODULES:
            if hasattr(module,name): setattr(module,name,value)
        super().__setattr__(name,value)
sys.modules[__name__].__class__ = _Facade
