# supabase-schema-mcp

![MCP Inspector with supabase-schema-mcp](docs/mcp-inspector-screenshot.png)

An MCP (Model Context Protocol) server that provides **deep schema introspection** for Supabase/Postgres projects. It complements the [official Supabase MCP](https://github.com/supabase/supabase-mcp) by focusing on detailed schema metadata: tables, columns, views, enums, RLS policies, functions/RPCs, foreign keys, indexes, and triggers. It does not duplicate high-level project or API features; it goes deeper on database structure for tooling and documentation.

## How this complements the official Supabase MCP

The official Supabase MCP covers project overview, branches, and API usage. This server is intentionally scoped to **introspection only**: it connects to your Supabase Postgres (and optionally the Management API) to expose schema details that help with migrations, RLS audits, relationship graphs, and RPC/trigger discovery. Use the official MCP for project management; use this one when you need fine-grained schema information.

## Tool list

| Tool | Description |
|------|-------------|
| `schema_list_tables` | List tables (optionally `schema_name='all'` for all user schemas). |
| `schema_list_columns` | List columns; optional `table_name` to restrict to one table. |
| `schema_list_views` | List views in the schema. |
| `schema_list_enums` | List custom enum types. |
| `rls_list_policies` | List RLS policies (table, policy, command, USING/WITH CHECK). |
| `rls_list_coverage` | Report which tables have RLS enabled and policy counts. |
| `functions_list` | List Postgres functions (signature, return type). |
| `functions_list_rpc_candidates` | List functions that are typical Supabase RPC candidates. |
| `relationships_list_foreign_keys` | List foreign key constraints. |
| `relationships_list_indexes` | List indexes; optional `table_name` filter. |
| `triggers_list` | List triggers; optional `table_name` filter. |

All tools accept `schema_name` (default `"public"`); use `schema_name="all"` to include all user schemas (excluding `pg_catalog` and `information_schema`).

## Setup

1. Clone the repo and **cd into the project directory** (the `supabase-schema-mcp` folder). All commands below must be run from this directory.
2. Create a virtual environment and install dependencies with **uv**:
   ```bash
   uv sync --extra dev
   ```
3. Copy `.env.example` to `.env` and set your Supabase Postgres connection:
   - **Required**: `SUPABASE_DB_HOST` (e.g. `db.<project_ref>.supabase.co`), `SUPABASE_DB_USER` (usually `postgres`), `SUPABASE_DB_PASSWORD` (from Project Settings > Database)
   - Optional: `SUPABASE_DB_PORT`, `SUPABASE_DB_NAME`
4. From the **same project directory**, run the MCP server over stdio:
   ```bash
   uv run python -m supabase_schema_mcp.server
   ```
   Or use the script entry point:
   ```bash
   uv run supabase-schema-mcp
   ```

### Adding as an MCP in Cursor

1. Open Cursor **Settings** (e.g. **Cursor > Settings** or `Cmd+,`).
2. Search for **MCP** or open **Features > MCP**.
3. Add this server via the JSON config. Edit **`~/.cursor/mcp.json`** (or your project's `.cursor/mcp.json`) and add a `supabase-schema-mcp` entry under `mcpServers`. Replace `PATH_TO_SUPABASE_SCHEMA_MCP` with the full path to this repo (the folder that contains `pyproject.toml` and `src/`):

   ```json
   {
     "mcpServers": {
       "supabase-schema-mcp": {
         "command": "uv",
         "args": [
           "--directory",
           "PATH_TO_SUPABASE_SCHEMA_MCP",
           "run",
           "python",
           "-m",
           "supabase_schema_mcp.server"
         ]
       }
     }
   }
   ```

   Example with a real path (macOS):

   ```json
   {
     "mcpServers": {
       "supabase-schema-mcp": {
         "command": "uv",
         "args": [
           "--directory",
           "/Users/you/Developer/supabase-schema-mcp",
           "run",
           "python",
           "-m",
           "supabase_schema_mcp.server"
         ]
       }
     }
   }
   ```

4. Restart Cursor (MCP servers load at startup). When the server starts, you should see on stderr: `supabase-schema-mcp server started (stdio)`. Any config warnings appear in a yellow panel above that.

5. You do **not** need to run the server in a terminal yourself. Cursor starts and manages the process when it needs to call the tools.

## Read-only safety model

This MCP server is designed to **read** schema and metadata only. It does not execute arbitrary writes or DDL. Database access should use a **read-only** Postgres role where possible; the connection layer enforces that only introspection-style, read-only operations are performed. Management API usage is limited to reading project/config data as needed. Never put a role with write or DDL privileges into this server's configuration unless you explicitly require it for a future feature.

## License

MIT. See [LICENSE](LICENSE).
