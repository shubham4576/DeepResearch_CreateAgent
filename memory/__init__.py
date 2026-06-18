from functools import lru_cache

from .base import BaseMemoryStore
from .in_memory_store import InMemoryStore
from .tool_logging import log_tool_call


@lru_cache
def get_memory_store() -> BaseMemoryStore:
    from config import config

    if config.MONGO_URI:
        from .mongodb_store import MongoMemoryStore

        return MongoMemoryStore(
            mongo_uri=config.MONGO_URI,
            db_name=config.MONGO_DB_NAME,
        )

    return InMemoryStore()


__all__ = [
    "BaseMemoryStore",
    "InMemoryStore",
    "get_memory_store",
    "log_tool_call",
]
