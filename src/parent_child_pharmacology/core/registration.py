"""Apply named input contracts, output envelopes, and protocol annotations."""

import functools
import json

from mcp.server.fastmcp.tools import Tool
from mcp.server.fastmcp.utilities.func_metadata import FuncMetadata
from mcp.types import CallToolResult, TextContent, ToolAnnotations

from parent_child_pharmacology.core.audit import audited
from parent_child_pharmacology.models.contracts import EvidenceResponse
from parent_child_pharmacology.models.inputs import INPUT_MODELS
from parent_child_pharmacology.services.descriptions import description


def register_tool(catalog, implementation, domain):
    name = implementation.__name__
    wrapped = audited(implementation)
    wrapped.__doc__ = description(name, implementation.__doc__, domain)

    @functools.wraps(wrapped)
    async def protocol_call(response_format="json", **kwargs):
        from .auth import authorize_tool
        from .pagination import add_pagination

        authorize_tool(name, catalog.auth_required)
        result = add_pagination(await wrapped(**kwargs), name, kwargs)
        if response_format == "markdown":
            # Escape all source text inside JSON blocks; no upstream HTML execution.
            # Include every field, not an abridged summary that can lose caveats.
            serialized = json.dumps(result, ensure_ascii=False, indent=2)
            fence = "`" * (
                max([len(s) for s in __import__("re").findall(r"`+", serialized)] or [2]) + 1
            )
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"## {name}\n\nUntrusted source data; preserve safety notices.\n\n{fence}json\n{serialized}\n{fence}",
                    )
                ],
                structuredContent=EvidenceResponse.model_validate(result).model_dump(mode="json"),
            )
        return result

    catalog.append(
        Tool(
            fn=protocol_call,
            name=name,
            description=wrapped.__doc__,
            is_async=True,
            parameters=INPUT_MODELS[name].model_json_schema(by_alias=True),
            fn_metadata=FuncMetadata(
                arg_model=INPUT_MODELS[name],
                output_model=EvidenceResponse,
                output_schema=EvidenceResponse.model_json_schema(),
            ),
            annotations=ToolAnnotations(
                readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True
            ),
        )
    )
    return wrapped


class ToolCatalog(list):
    """Construct documented SDK Tool objects before FastMCP(tools=...)."""

    def __init__(self, auth_required=False):
        super().__init__()
        self.auth_required = auth_required
