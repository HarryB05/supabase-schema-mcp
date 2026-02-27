"""Postgres function and RPC introspection tools."""

import json

from supabase_schema_mcp.db import fetch_all


async def list_functions(schema_name: str = "public") -> str:
    """
    List functions and procedures: schema, name, argument types, return type,
    and whether they are callable (security definer, etc.).
    Includes functions that can be exposed as Supabase RPCs.
    """
    if schema_name == "all":
        schema_filter = "AND n.nspname NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND n.nspname = $1"
        args = (schema_name,)
    query = f"""
        SELECT n.nspname AS schema_name, p.proname AS function_name,
               pg_get_function_arguments(p.oid) AS arguments,
               pg_get_function_result(p.oid) AS return_type,
               p.prosecdef AS security_definer,
               p.provolatile AS volatility
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
        {schema_filter}
        ORDER BY n.nspname, p.proname
    """
    rows = await fetch_all(query, *args)
    result = [
        {
            "schema": r["schema_name"],
            "function": r["function_name"],
            "arguments": r["arguments"],
            "return_type": r["return_type"],
            "security_definer": r["security_definer"],
            "volatility": _volatility_str(r["volatility"]),
        }
        for r in rows
    ]
    return json.dumps(result, indent=2)


def _volatility_str(v: str | None) -> str:
    """Map pg_proc.provolatile to string."""
    mapping = {"i": "IMMUTABLE", "s": "STABLE", "v": "VOLATILE"}
    return mapping.get(v or "", v or "unknown")


async def list_rpc_candidates(schema_name: str = "public") -> str:
    """
    List functions in the given schema that are typical RPC candidates:
    return type suitable for JSON (record, void, scalar), in public or specified schema.
    """
    if schema_name == "all":
        schema_filter = "AND n.nspname NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND n.nspname = $1"
        args = (schema_name,)
    query = f"""
        SELECT n.nspname AS schema_name, p.proname AS function_name,
               pg_get_function_arguments(p.oid) AS arguments,
               pg_get_function_result(p.oid) AS return_type
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
        {schema_filter}
        ORDER BY n.nspname, p.proname
    """
    rows = await fetch_all(query, *args)
    result = [
        {
            "schema": r["schema_name"],
            "function": r["function_name"],
            "arguments": r["arguments"],
            "return_type": r["return_type"],
        }
        for r in rows
    ]
    return json.dumps(result, indent=2)
