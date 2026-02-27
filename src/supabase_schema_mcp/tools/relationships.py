"""Foreign key and index introspection tools."""

import json
from typing import Any

from supabase_schema_mcp.db import fetch_all


async def list_foreign_keys(schema_name: str = "public") -> str:
    """
    List foreign key constraints: from table/columns, to table/columns,
    constraint name, and update/delete rule.
    """
    if schema_name == "all":
        schema_filter = (
            "AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')"
        )
        args: tuple = ()
    else:
        schema_filter = "AND tc.table_schema = $1"
        args = (schema_name,)
    query = f"""
        SELECT tc.table_schema AS from_schema, tc.table_name AS from_table,
               kcu.column_name AS from_column,
               ccu.table_schema AS to_schema, ccu.table_name AS to_table,
               ccu.column_name AS to_column,
               tc.constraint_name, rc.update_rule, rc.delete_rule
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
             ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
             ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
        JOIN information_schema.referential_constraints rc
             ON tc.constraint_name = rc.constraint_name
             AND tc.table_schema = rc.constraint_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        {schema_filter}
        ORDER BY tc.table_schema, tc.table_name, tc.constraint_name
    """
    rows = await fetch_all(query, *args)
    result = [
        {
            "from_schema": r["from_schema"],
            "from_table": r["from_table"],
            "from_column": r["from_column"],
            "to_schema": r["to_schema"],
            "to_table": r["to_table"],
            "to_column": r["to_column"],
            "constraint_name": r["constraint_name"],
            "on_update": r["update_rule"],
            "on_delete": r["delete_rule"],
        }
        for r in rows
    ]
    return json.dumps(result, indent=2)


async def list_indexes(
    schema_name: str = "public",
    table_name: str | None = None,
) -> str:
    """
    List indexes: schema, table, index name, columns, uniqueness, definition.
    Optionally filter by table_name.
    """
    if schema_name == "all":
        schema_filter = "AND n.nspname NOT IN ('pg_catalog', 'information_schema')"
        args: tuple = ()
    else:
        schema_filter = "AND n.nspname = $1"
        args = (schema_name,)
    if table_name:
        table_filter = "AND c.relname = $" + str(len(args) + 1)
        args = (*args, table_name)
    else:
        table_filter = ""
    query = f"""
        SELECT n.nspname AS schema_name, c.relname AS table_name,
               i.relname AS index_name, a.attname AS column_name,
               ix.indisunique AS is_unique, ix.indisprimary AS is_primary,
               pg_get_indexdef(ix.indexrelid) AS definition
        FROM pg_index ix
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_class c ON c.oid = ix.indrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(ix.indkey)
            AND a.attnum > 0 AND NOT a.attisdropped
        WHERE c.relkind IN ('r', 'm')
        {schema_filter}
        {table_filter}
        ORDER BY n.nspname, c.relname, i.relname, array_position(ix.indkey, a.attnum)
    """
    rows = await fetch_all(query, *args)
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for r in rows:
        key = (r["schema_name"], r["table_name"], r["index_name"])
        if key not in by_key:
            by_key[key] = {
                "schema": r["schema_name"],
                "table": r["table_name"],
                "index": r["index_name"],
                "columns": [r["column_name"]],
                "is_unique": r["is_unique"],
                "is_primary": r["is_primary"],
                "definition": r["definition"],
            }
        else:
            by_key[key]["columns"].append(r["column_name"])
    result = list(by_key.values())
    return json.dumps(result, indent=2)
