"""Apply named input contracts, output envelopes, and protocol annotations."""

from mcp.types import ToolAnnotations

from parent_child_pharmacology.core.audit import audited
from parent_child_pharmacology.models.inputs import INPUT_MODELS
from parent_child_pharmacology.services.descriptions import description


def register_tool(mcp, implementation, domain):
    name = implementation.__name__
    wrapped = audited(implementation)
    wrapped.__doc__ = description(name, implementation.__doc__, domain)
    mcp.add_tool(
        wrapped,
        structured_output=True,
        annotations=ToolAnnotations(
            readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True
        ),
    )
    registered = mcp._tool_manager.get_tool(name)
    registered.fn_metadata.arg_model = INPUT_MODELS[name]
    registered.parameters = INPUT_MODELS[name].model_json_schema(by_alias=True)
    return wrapped
