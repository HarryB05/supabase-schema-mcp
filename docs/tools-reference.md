# Tool reference

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
