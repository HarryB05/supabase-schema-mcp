"""RLS policy and coverage tools."""

import json

from supabase_schema_mcp.db import fetch_all


async def list_rls_policies(schema_name: str = "public") -> str:
    """
    List Row Level Security policies: table, policy name, command (SELECT/INSERT/etc),
    permissive/restrictive, and the USING/WITH CHECK expressions.
    """
    if schema_name == "all":
        schema_filter = "AND n.nspname NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND n.nspname = $1"
        args = (schema_name,)
    query = f"""
        SELECT n.nspname AS schema_name, c.relname AS table_name,
               p.polname AS policy_name, p.polcmd AS command,
                CASE p.polpermissive
                    WHEN true THEN 'PERMISSIVE' ELSE 'RESTRICTIVE'
                END AS type,
               pg_get_expr(p.polqual, p.polrelid) AS using_expr,
               pg_get_expr(p.polwithcheck, p.polrelid) AS with_check_expr
        FROM pg_policy p
        JOIN pg_class c ON c.oid = p.polrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r'
        {schema_filter}
        ORDER BY n.nspname, c.relname, p.polname
    """
    rows = await fetch_all(query, *args)
    result = [
        {
            "schema": r["schema_name"],
            "table": r["table_name"],
            "policy": r["policy_name"],
            "command": _polcmd_to_str(r["command"]),
            "type": r["type"],
            "using": r["using_expr"],
            "with_check": r["with_check_expr"],
        }
        for r in rows
    ]
    return json.dumps(result, indent=2)


def _polcmd_to_str(cmd: str | None) -> str:
    """Map pg_policy.polcmd to human-readable command."""
    if cmd is None:
        return "ALL"
    return {"r": "SELECT", "a": "INSERT", "w": "UPDATE", "d": "DELETE", "*": "ALL"}.get(
        cmd, str(cmd)
    )


async def list_rls_coverage(schema_name: str = "public") -> str:
    """
    Report which tables have RLS enabled and how many policies they have.
    Useful for auditing RLS coverage.
    """
    if schema_name == "all":
        schema_filter = "AND n.nspname NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND n.nspname = $1"
        args = (schema_name,)
    query = f"""
        SELECT n.nspname AS schema_name, c.relname AS table_name,
               c.relrowsecurity AS rls_enabled,
                (SELECT count(*) FROM pg_policy p WHERE p.polrelid = c.oid)
                    AS policy_count
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r'
        {schema_filter}
        ORDER BY n.nspname, c.relname
    """
    rows = await fetch_all(query, *args)
    result = [
        {
            "schema": r["schema_name"],
            "table": r["table_name"],
            "rls_enabled": r["rls_enabled"],
            "policy_count": r["policy_count"],
        }
        for r in rows
    ]
    return json.dumps(result, indent=2)
