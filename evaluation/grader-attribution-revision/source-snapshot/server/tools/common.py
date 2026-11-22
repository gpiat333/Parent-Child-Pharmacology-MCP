import logging
from core import config as cfg
log=logging.getLogger("mc")
async def _lakehouse_or_none(coro):
    """Run a lakehouse query; return None (-> live fallback) if unavailable or empty."""
    if not cfg.USE_LAKEHOUSE:
        coro.close()
        return None
    try:
        return await coro
    except Exception as e:
        log.warning("lakehouse unavailable, falling back to live (%s)", type(e).__name__)
        return None
