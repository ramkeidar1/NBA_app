import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_API_SECRECT_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_API_SECRECT_KEY must be set in .env")
        _client = create_client(url, key)
        logger.info("Supabase client initialised")
    return _client
