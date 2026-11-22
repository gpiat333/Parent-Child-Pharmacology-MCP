"""Public-source adapters. Compatibility exports preserve existing callers."""

import sys
from importlib import import_module
from types import ModuleType

_MODULES = [
    import_module(__name__ + "." + name)
    for name in [
        "parsing",
        "ncbi",
        "lactmed",
        "pubmed",
        "rxnorm",
        "dailymed",
        "clinicaltrials",
        "reporter",
        "openfda",
        "medlineplus",
    ]
]


def __getattr__(name):
    for module in _MODULES:
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(name)


class _Facade(ModuleType):
    def __setattr__(self, name, value):
        for module in _MODULES:
            if hasattr(module, name):
                setattr(module, name, value)
        super().__setattr__(name, value)


# Materialize compatibility exports so monkeypatch/introspection can restore them.
for _module in _MODULES:
    for _name, _value in vars(_module).items():
        if not _name.startswith("__") and _name not in globals():
            globals()[_name] = _value
sys.modules[__name__].__class__ = _Facade
