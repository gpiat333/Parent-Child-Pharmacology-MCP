from importlib import import_module


def register_resources(mcp):
    for name in ["data_sources", "source_capabilities", "mprint_snapshot", "disclaimer"]:
        import_module(__name__ + "." + name).register(mcp)
