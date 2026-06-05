# Protection Profile Options

This guide explains the three protection-profile patterns supported in this repository:

- global-column based profiles using `column.<column>.profile`
- global-column-legacy based profiles using `COLUMN_PROFILES`
- table-column based profiles using `protect.object.<object>`

It also explains when each option is a good fit and which mapping takes precedence if both are configured.

It also explains when each option is a good fit and which mapping takes precedence if more than one is configured.

## Three profile styles

### Option 1: Global-column based profiles

This is the newer structured global form.

Example:

```properties
column.email.profile=tag.char.internal
column.address.profile=tag.char.internal
column.ssn.profile=tag.nbr.internal
```

This approach is best when:

- one logical column name maps to one policy across the environment
- teams want a structured per-column property model
- future per-column options such as metadata or reveal-user overrides may also be needed

### Option 2: Global-column-legacy based profiles

This works well when customers use the same logical column names across many tables and want those columns to resolve to the same protection profile everywhere.

Example:

- every `email` column in the environment should use the same profile
- every `ssn` column should use the same profile
- all systems are ready to protect and reveal those fields consistently

In that case, a global mapping is simple and effective.

Example:

```properties
COLUMN_PROFILES=email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal
```

This approach is best when:

- one logical column name maps to one policy across the environment
- teams want simpler configuration
- table-specific variation is not needed

This is the older compact global form.

### Option 3: Table-column based profiles

This works better when organizations cannot apply the same profile to every table at the same time.

Typical examples:

- one core customer table is protected first, but downstream tables are not ready yet
- one team wants internal protection for `email`, while another table needs external or none protection
- the same business column names appear in multiple protected table variants

Example:

- `my_catalog.my_schema.customer_protected_internal.email` should use one profile
- `my_catalog.my_schema.customer_protected_external.email` should use another
- `my_catalog.my_schema.customer_protected_none.email` should use a third

In that case, object-specific mapping is the better fit.

Example:

```properties
protect.object.my_catalog.my_schema.customer_protected_internal=email|tag.char.internal
protect.object.my_catalog.my_schema.customer_protected_external=email|tag.char.external
protect.object.my_catalog.my_schema.customer_protected_none=email|tag.char.none
```

This approach is best when:

- the same logical column names must resolve differently by table
- protection rollout happens table by table
- downstream systems are migrating at different speeds
- customers want different profiles for different protected objects

## How table-column based mappings work

Table-column based mappings use this format:

```properties
protect.object.<catalog>.<schema>.<table>=column|tag...,column|tag...
```

Examples already included in the repository:

```properties
protect.object.my_catalog.my_schema.plaintext_protected_internal=email|tag.char.internal,address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal
protect.object.my_catalog.my_schema.plaintext_protected_external=email|tag.char.external,address|tag.char.external,ssn|tag.nbr.external,creditcard|tag.nbr.external,creditcardcode|tag.nbr.external
protect.object.my_catalog.my_schema.plaintext_protected_none=email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none,creditcard|tag.nbr.none,creditcardcode|tag.nbr.none

protect.object.my_catalog.my_schema.account_balance_numbers_protected_internal=balance|tag.nbr.internal,amount|tag.nbr.internal,fee|tag.nbr.internal
protect.object.my_catalog.my_schema.account_balance_numbers_protected_external=balance|tag.nbr.external,amount|tag.nbr.external,fee|tag.nbr.external
protect.object.my_catalog.my_schema.account_balance_numbers_protected_none=balance|tag.nbr.none,amount|tag.nbr.none,fee|tag.nbr.none
```

These mappings are defined in:
- [udfConfig.properties](E:\eclipse-workspace\thales.databricks.udf\src\main\resources\udfConfig.properties)

## Why the object name must be explicit

A global function call such as:

```sql
thales_protect_by_column(CAST(email AS STRING), 'char', 'email')
```

passes only:

- the value
- the datatype
- the logical column name

That works well for the global use case, but it does not distinguish between:

- `my_catalog.my_schema.customer_protected_internal.email`
- `my_catalog.my_schema.customer_protected_external.email`

To support different profiles by table, the object name must be included in the call.

Example:

```sql
thales_protect_by_object_and_column(
  CAST(email AS STRING),
  'char',
  'my_catalog.my_schema.customer_protected_external',
  'email'
)
```

## Order of precedence

If more than one mapping style is configured, the runtime resolves protection profiles in this order:

1. `protect.object.<object>`
2. `column.<column>.profile`
3. `COLUMN_PROFILES`
4. default datatype-based fallback policies

That means:

- if a matching `protect.object.<catalog>.<schema>.<table>` entry exists for the object and column, that mapping is used first
- if not, the runtime looks for `column.<column>.profile`
- if that is not present, the runtime falls back to `COLUMN_PROFILES`
- if none of those are configured, the runtime falls back to the default internal or external datatype-based policy settings

This is the key reason customers can safely define all three:

- global defaults for broad reuse
- object-specific overrides for exceptions and phased rollout
- legacy compact mappings for backward compatibility

## Recommended mental model

Think of it like this:

- `protect.object...` = table-level override where needed
- `column.<column>.profile` = structured global default
- `COLUMN_PROFILES` = legacy global fallback

That gives customers a clean rollout model:

- start with global mappings when everything is uniform
- add object-specific mappings only where a table needs different behavior

## Function families to use

### Use global column-aware functions when global mapping is enough

- `thales_protect_by_column(...)`
- `thales_reveal_by_column_with_user(...)`
- `thales_reveal_bulk_by_column_with_user(...)`
- `thales_protect_by_column_with_external_header(...)`
- `thales_reveal_by_column_with_external_header_and_user(...)`
- `thales_reveal_bulk_by_column_with_external_header_and_user(...)`

### Use object-aware functions when table-specific mapping is needed

- `thales_protect_by_object_and_column(value, datatype, object_name, column_name)`
- `thales_reveal_by_object_and_column_with_user(value, datatype, object_name, column_name, reveal_user)`
- `thales_reveal_bulk_by_object_and_column_with_user(values, datatype, object_name, column_name, reveal_user)`
- `thales_protect_by_object_and_column_with_external_header(value, datatype, object_name, column_name)`
- `thales_reveal_by_object_and_column_with_external_header_and_user(value, external_header, datatype, object_name, column_name, reveal_user)`
- `thales_reveal_bulk_by_object_and_column_with_external_header_and_user(values, external_headers, datatype, object_name, column_name, reveal_user)`

## Compute cluster examples

Object-aware examples are used in:

- [plaintext_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\plaintext_setup.sql)
- [numbers_setup.sql](E:\eclipse-workspace\thales.databricks.udf\notebooks\numbers\numbers_setup.sql)
- [compute_cluster_udf_smoke_test.py](E:\eclipse-workspace\thales.databricks.udf\notebooks\compute_cluster_udf_smoke_test.py)

Example:

```sql
thales_reveal_by_object_and_column_with_user(
  CAST(balance_long AS STRING),
  'nbr',
  'my_catalog.my_schema.account_balance_numbers_protected_internal',
  'balance',
  current_user()
)
```

## SQL Warehouse examples

SQL Warehouse follows the same object-aware model through Python-backed Unity Catalog functions and generated reveal views.

Relevant files:

- [create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_internal_reveal_functions_and_views_embedded_config.sql)
- [create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\deploy\create_uc_plaintext_protected_external_reveal_functions_and_views_embedded_config.sql)
- [generate_reveal_views_from_properties.py](E:\eclipse-workspace\thales.databricks.udf\sql_warehouse\utils\generate_reveal_views_from_properties.py)

The SQL Warehouse generator reads `protect.object.<catalog>.<schema>.<table>` entries and uses them to build reveal-view SQL for the corresponding protected tables.

## Practical recommendation

Use `column.<column>.profile` when:

- all tables should resolve the same profile for the same business column
- you want the preferred structured global format
- you may later want other per-column properties next to the profile mapping

Use `COLUMN_PROFILES` when:

- you are maintaining older configurations
- you want the compact legacy format for simple global defaults
- backward compatibility matters more than structure

Use `protect.object.<object>` when:

- rollout is phased table by table
- downstream systems are not all ready yet
- different teams or datasets need different profiles for the same logical column names
- internal, external, and none-protection variants coexist in the same environment

## Operational summary

If multiple mapping styles are present:

- `protect.object.<object>` takes precedence
- `column.<column>.profile` is the next global fallback
- `COLUMN_PROFILES` is the legacy global fallback after that

That makes it safe to support both:

- broad environment-wide defaults
- targeted table-level overrides
- older compact global mappings during migration

This is the supported way in this repository to handle customer environments where protection policy selection is either:

- globally consistent
- or intentionally different by protected table
