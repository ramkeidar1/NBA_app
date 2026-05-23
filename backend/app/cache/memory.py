import time
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from app.schemas import FormEvalJSON, MatchupEvalJSON

V = TypeVar("V")


class TTLCache(Generic[V]):
    def __init__(self, ttl_seconds: float) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[V, float]] = {}

    def get(self, key: str) -> V | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: V) -> None:
        self._store[key] = (value, time.monotonic() + self._ttl)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


# Module-level singletons — 1-hour TTL matches typical game-day staleness tolerance
form_cache: "TTLCache[FormEvalJSON]" = TTLCache(ttl_seconds=3600)
matchup_cache: "TTLCache[MatchupEvalJSON]" = TTLCache(ttl_seconds=3600)
