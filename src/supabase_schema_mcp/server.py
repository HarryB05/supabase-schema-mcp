"""MCP server entry point and tool registration."""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from supabase_schema_mcp.config import get_env_warnings
from supabase_schema_mcp.tools import functions as tools_functions
from supabase_schema_mcp.tools import relationships as tools_relationships
from supabase_schema_mcp.tools import rls as tools_rls
from supabase_schema_mcp.tools import schema as tools_schema
from supabase_schema_mcp.tools import triggers as tools_triggers

mcp = FastMCP(
    "supabase-schema-mcp",
    json_response=True,
)


# ---- Schema tools ----
@mcp.tool()
async def schema_list_tables(schema_name: str = "public") -> str:
    """List tables in the schema (default: public). Use schema_name='all' for all."""
    return await tools_schema.list_tables(schema_name)


@mcp.tool()
async def schema_list_columns(
    schema_name: str = "public",
    table_name: str | None = None,
) -> str:
    """List columns for tables in the schema. Optionally restrict to one table."""
    return await tools_schema.list_columns(schema_name, table_name)


@mcp.tool()
async def schema_list_views(schema_name: str = "public") -> str:
    """List views in the given schema. Use schema_name='all' for all user schemas."""
    return await tools_schema.list_views(schema_name)


@mcp.tool()
async def schema_list_enums(schema_name: str = "public") -> str:
    """List custom enum types. Use schema_name='all' for all user schemas."""
    return await tools_schema.list_enums(schema_name)


# ---- RLS tools ----
@mcp.tool()
async def rls_list_policies(schema_name: str = "public") -> str:
    """List RLS policies (table, policy, command). schema_name='all' for all schemas."""
    return await tools_rls.list_rls_policies(schema_name)


@mcp.tool()
async def rls_list_coverage(schema_name: str = "public") -> str:
    """Report tables with RLS enabled and policy counts. schema_name='all' for all."""
    return await tools_rls.list_rls_coverage(schema_name)


@mcp.tool()
async def rls_get_policy(
    schema_name: str, table_name: str, policy_name: str
) -> str:
    """Return the definition (USING and WITH CHECK code) of an RLS policy by name."""
    return await tools_rls.get_rls_policy_definition(
        schema_name, table_name, policy_name
    )


# ---- Function / RPC tools ----
@mcp.tool()
async def functions_list(schema_name: str = "public") -> str:
    """List Postgres functions (signature, return type). schema_name='all' for all."""
    return await tools_functions.list_functions(schema_name)


@mcp.tool()
async def functions_list_rpc_candidates(schema_name: str = "public") -> str:
    """List Supabase RPC-callable function candidates. schema_name='all' for all."""
    return await tools_functions.list_rpc_candidates(schema_name)


@mcp.tool()
async def functions_get_definition(schema_name: str, function_name: str) -> str:
    """Return the full source code (CREATE FUNCTION) of an RPC/function by name."""
    return await tools_functions.get_function_definition(schema_name, function_name)


# ---- Relationship tools ----
@mcp.tool()
async def relationships_list_foreign_keys(schema_name: str = "public") -> str:
    """List foreign keys (from/to table and columns). schema_name='all' for all."""
    return await tools_relationships.list_foreign_keys(schema_name)


@mcp.tool()
async def relationships_list_indexes(
    schema_name: str = "public",
    table_name: str | None = None,
) -> str:
    """List indexes (table, index, columns). schema_name='all' for all schemas."""
    return await tools_relationships.list_indexes(schema_name, table_name)


# ---- Trigger tools ----
@mcp.tool()
async def triggers_list(
    schema_name: str = "public",
    table_name: str | None = None,
) -> str:
    """List triggers (table, trigger, timing, event). schema_name='all' for all."""
    return await tools_triggers.list_triggers(schema_name, table_name)


def _mcp_json_snippet() -> str:
    """Generate the mcpServers entry for this server with current directory."""
    project_dir = Path.cwd().resolve()
    entry = {
        "supabase-schema-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                str(project_dir),
                "run",
                "python",
                "-m",
                "supabase_schema_mcp.server",
            ],
        }
    }
    return json.dumps(entry, indent=2)


def run() -> None:
    """Run the MCP server over stdio (for Cursor and other MCP clients)."""
    stderr = Console(stderr=True)
    stderr.print(
        "[dim]supabase-schema-mcp server started (stdio)[/]",
        highlight=False,
    )
    snippet = _mcp_json_snippet()
    stderr.print(
        Panel(
            Syntax(snippet, "json", theme="monokai", line_numbers=False),
            title="[bold]Paste into [dim]~/.cursor/mcp.json[/] in mcpServers",
            border_style="blue",
        )
    )
    warnings = get_env_warnings()
    if warnings:
        content = "\n\n".join(warnings)
        stderr.print(
            Panel(
                content,
                title="[bold]supabase-schema-mcp[/] config warning",
                border_style="yellow",
            )
        )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
