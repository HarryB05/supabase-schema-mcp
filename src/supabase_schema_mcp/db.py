"""Asyncpg connection pool management and read-only role enforcement."""

import asyncio
from typing import Any, cast

import asyncpg

from supabase_schema_mcp.config import get_settings

_pool: asyncpg.Pool | None = None
_pool_lock = asyncio.Lock()


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Set read-only mode on new connections when configured."""
    settings = get_settings()
    if settings.db_read_only:
        await conn.execute("SET default_transaction_read_only = on")


async def get_pool() -> asyncpg.Pool:
    """Return the shared asyncpg pool, creating it on first use."""
    global _pool
    async with _pool_lock:
        if _pool is not None:
            return _pool
        settings = get_settings()
        if not settings.db_connection_configured:
            raise RuntimeError(
                "Database not configured. Set SUPABASE_DB_HOST, SUPABASE_DB_USER, "
                "SUPABASE_DB_PASSWORD (and optionally SUPABASE_DB_NAME, PORT) in .env"
            )
        _pool = await asyncpg.create_pool(
            host=settings.supabase_db_host,
            port=settings.supabase_db_port,
            database=settings.supabase_db_name,
            user=settings.supabase_db_user,
            password=settings.supabase_db_password,
            min_size=1,
            max_size=5,
            init=_init_connection,
            command_timeout=30,
            statement_cache_size=0
        )
        return _pool


async def close_pool() -> None:
    """Close the shared pool (e.g. on shutdown)."""
    global _pool
    async with _pool_lock:
        if _pool is not None:
            await _pool.close()
            _pool = None


async def fetch_one(
    query: str,
    *args: Any,
) -> asyncpg.Record | None:
    """Run a read-only query and return the first row. Uses shared pool."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def fetch_all(
    query: str,
    *args: Any,
) -> list[asyncpg.Record]:
    """Run a read-only query and return all rows. Uses shared pool."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        return cast(list[asyncpg.Record], await conn.fetch(query, *args))
