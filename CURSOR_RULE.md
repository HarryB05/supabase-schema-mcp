---
description: MUST use Supabase schema MCP for any schema introspection; never use raw SQL or guess.
alwaysApply: true
---

# Supabase schema MCP (mandatory)

**You MUST use the Supabase schema MCP** (server: `user-supabase-schema-mcp`) for any question or task about the database schema. Do not guess, infer from code, or run custom SQL or scripts for introspection.

## When to use it

Use the MCP tools **before** answering or writing code when the user (or the task) involves:

- **Tables**: listing tables, table names, "what tables exist", schema overview
- **Columns**: column names, types, nullable, defaults for any table
- **Views**: listing views or view definitions
- **Enums**: enum types and their values
- **RLS**: policies, policy coverage, "who can access what", or the **code** (USING/WITH CHECK) of a specific policy
- **Functions/RPCs**: stored functions, RPCs, procedure signatures, or the **source code** of a specific RPC/function
- **Relationships**: foreign keys, indexes
- **Triggers**: trigger definitions
- **Migrations or schema design**: before writing or reviewing migrations, confirm current schema with the MCP

When in doubt, call the MCP first.

## Tools to use

- `schema_list_tables` – tables (use `schema_name: 'all'` for all schemas)
- `schema_list_columns` – columns for a table
- `schema_list_views` – views
- `schema_list_enums` – enum types
- `rls_list_policies` – RLS policies
- `rls_list_coverage` – RLS coverage
- `rls_get_policy` – RLS policy definition (USING/WITH CHECK code) by schema, table and policy name
- `functions_list` / `functions_list_rpc_candidates` – functions/RPCs
- `functions_get_definition` – full source code (CREATE FUNCTION) of an RPC/function by schema and name
- `relationships_list_foreign_keys` – foreign keys
- `relationships_list_indexes` – indexes
- `triggers_list` – triggers

Check each tool’s descriptor in `mcps/user-supabase-schema-mcp/tools/*.json` before calling if needed.

## What not to do

- Do **not** run `psql`, `supabase db dump`, or custom `SELECT` queries for schema introspection.
- Do **not** answer schema questions from memory or from reading only application code; use the MCP result.
