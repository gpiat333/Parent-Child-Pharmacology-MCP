"""parsing public-source adapter; no MCP registration."""

import re
import xml.etree.ElementTree as ET


def text_of(el: ET.Element | None) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else ""
