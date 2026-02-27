# Supabase schema MCP

When the user asks about their **Supabase (or Postgres) database schema** — e.g. tables, columns, views, enums, RLS policies, triggers, functions/RPCs, foreign keys, or indexes — use the **supabase-schema-mcp** MCP server and its tools. Do not run custom SQL or scripts for schema introspection; use these tools instead.

Relevant tools: `schema_list_tables`, `schema_list_columns`, `schema_list_views`, `schema_list_enums`, `rls_list_policies`, `rls_list_coverage`, `functions_list`, `functions_list_rpc_candidates`, `relationships_list_foreign_keys`, `relationships_list_indexes`, `triggers_list`.