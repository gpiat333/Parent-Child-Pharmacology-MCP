"""parsing public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http



def text_of(el: ET.Element | None) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else ""
