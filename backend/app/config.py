import logging
import os

from dotenv import load_dotenv

load_dotenv()

# ── DUMMY_MODE ────────────────────────────────────────────────────────────────
# Set DUMMY_MODE=false in .env to run real LLM calls.
# Defaults to True so the app works out of the box without API spend.
DUMMY_MODE: bool = os.getenv("DUMMY_MODE", "true").lower() != "false"

# ── Logging ───────────────────────────────────────────────────────────────────
# Set LOG_LEVEL=DEBUG | INFO | WARNING | ERROR in .env.
_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
_level = getattr(logging, _level_name, logging.INFO)

logging.basicConfig(
    level=_level,
    format="%(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)
logger.info("Config loaded — DUMMY_MODE=%s  LOG_LEVEL=%s", DUMMY_MODE, _level_name)
