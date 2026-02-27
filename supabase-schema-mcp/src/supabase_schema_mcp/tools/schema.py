"""Table, column, view, and enum introspection tools."""

import json

from supabase_schema_mcp.db import fetch_all


async def list_tables(schema_name: str = "public") -> str:
    """
    List tables in the given schema (default: public).
    Returns table names and table type (BASE TABLE).
    """
    if schema_name == "all":
        schema_filter = "AND t.table_schema NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND t.table_schema = $1"
        args = (schema_name,)
    query = f"""
        SELECT t.table_schema, t.table_name, t.table_type
        FROM information_schema.tables t
        WHERE t.table_type = 'BASE TABLE'
        {schema_filter}
        ORDER BY t.table_schema, t.table_name
    """
    rows = await fetch_all(query, *args)
    result = [
        {"schema": r["table_schema"], "table": r["table_name"], "type": r["table_type"]}
        for r in rows
    ]
    return json.dumps(result, indent=2)


async def list_columns(
    schema_name: str = "public",
    table_name: str | None = None,
) -> str:
    """
    List columns for tables in the given schema.
    If table_name is provided, only that table's columns are returned.
    """
    if schema_name == "all":
        schema_filter = "AND c.table_schema NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND c.table_schema = $1"
        args = (schema_name,)
    if table_name:
        table_filter = "AND c.table_name = $" + str(len(args) + 1)
        args = (*args, table_name)
    else:
        table_filter = ""
    query = f"""
        SELECT c.table_schema, c.table_name, c.column_name, c.data_type,
               c.is_nullable, c.column_default
        FROM information_schema.columns c
        WHERE 1=1
        {schema_filter}
        {table_filter}
        ORDER BY c.table_schema, c.table_name, c.ordinal_position
    """
    rows = await fetch_all(query, *args)
    result = [
        {
            "schema": r["table_schema"],
            "table": r["table_name"],
            "column": r["column_name"],
            "data_type": r["data_type"],
            "nullable": r["is_nullable"] == "YES",
            "default": r["column_default"],
        }
        for r in rows
    ]
    return json.dumps(result, indent=2)


async def list_views(schema_name: str = "public") -> str:
    """List views in the given schema (default: public)."""
    if schema_name == "all":
        schema_filter = "AND v.table_schema NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND v.table_schema = $1"
        args = (schema_name,)
    query = f"""
        SELECT v.table_schema, v.table_name, v.view_definition
        FROM information_schema.views v
        WHERE 1=1
        {schema_filter}
        ORDER BY v.table_schema, v.table_name
    """
    rows = await fetch_all(query, *args)
    result = []
    for r in rows:
        full_def = r["view_definition"] or ""
        preview = full_def[:500] + ("..." if len(full_def) > 500 else "")
        result.append({
            "schema": r["table_schema"],
            "view": r["table_name"],
            "definition_preview": preview,
        })
    return json.dumps(result, indent=2)


async def list_enums(schema_name: str = "public") -> str:
    """List custom enum types in the given schema (default: public)."""
    if schema_name == "all":
        schema_filter = "AND n.nspname NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND n.nspname = $1"
        args = (schema_name,)
    query = f"""
        SELECT n.nspname AS schema_name, t.typname AS enum_name,
               array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_labels
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE t.typtype = 'e'
        {schema_filter}
        GROUP BY n.nspname, t.typname
        ORDER BY n.nspname, t.typname
    """
    rows = await fetch_all(query, *args)
    result = [
        {
            "schema": r["schema_name"],
            "enum": r["enum_name"],
            "labels": list(r["enum_labels"]) if r["enum_labels"] else [],
        }
        for r in rows
    ]
    return json.dumps(result, indent=2)
