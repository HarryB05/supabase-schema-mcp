"""Trigger introspection tools."""

import json

from supabase_schema_mcp.db import fetch_all


async def list_triggers(
    schema_name: str = "public",
    table_name: str | None = None,
) -> str:
    """
    List triggers: schema, table, trigger name, timing, events, function.
    """
    if schema_name == "all":
        schema_filter = (
            "AND t.trigger_schema NOT IN ('pg_catalog', 'information_schema')"
        )
        args: tuple = ()
    else:
        schema_filter = "AND t.trigger_schema = $1"
        args = (schema_name,)
    if table_name:
        table_filter = "AND t.event_object_table = $" + str(len(args) + 1)
        args = (*args, table_name)
    else:
        table_filter = ""
    query = f"""
        SELECT t.trigger_schema AS schema_name, t.event_object_table AS table_name,
               t.trigger_name, t.action_timing AS timing, t.event_manipulation AS event,
               t.action_statement AS action_statement
        FROM information_schema.triggers t
        WHERE 1=1
        {schema_filter}
        {table_filter}
        ORDER BY t.trigger_schema, t.event_object_table, t.trigger_name
    """
    rows = await fetch_all(query, *args)
    result = [
        {
            "schema": r["schema_name"],
            "table": r["table_name"],
            "trigger": r["trigger_name"],
            "timing": r["timing"],
            "event": r["event"],
            "action": r["action_statement"],
        }
        for r in rows
    ]
    return json.dumps(result, indent=2)
