# Reveal User Override Guide

## Purpose

This guide explains how `REVEAL_USER_OVERRIDE_ALLOWED` affects reveal behavior in
the Python helper wheel, including:

- DataFrame helper APIs such as `reveal_dataframe(...)`
- row-based helper APIs such as `reveal_rows(...)`
- Unity Catalog-oriented Python wheel APIs such as
  `uc_reveal_by_object_and_column(...)`

## Short answer

`REVEAL_USER_OVERRIDE_ALLOWED` controls whether the caller is allowed to supply
an explicit reveal user for Python helper reveal paths.

### When it is `true`

The caller can override reveal-user resolution.

### When it is `false`

The caller cannot override reveal-user resolution, and the helper falls back to
its locked runtime behavior.

## What it does not apply to

It does **not** apply to protect APIs, because protect does not use a reveal
user.

Examples where it does **not** apply:

- `protect_dataframe(...)`
- `protect_rows(...)`
- `uc_protect_by_object_and_column(...)`
- `uc_protect_bulk_by_object_and_column(...)`

## What it does apply to

It does apply to reveal APIs such as:

- `reveal_dataframe(...)`
- `reveal_rows(...)`
- `uc_reveal_by_object_and_column(...)`
- `uc_reveal_bulk_by_object_and_column(...)`
- `uc_reveal_row(...)`
- `uc_reveal_rowset_embedded(...)`

## Configuration

The config loader accepts either of these property names:

```properties
REVEAL_USER_OVERRIDE_ALLOWED=true
```

or

```properties
ALLOW_REVEAL_USER_OVERRIDE=true
```

If not set, the current integration code defaults to `true`.

## DataFrame helper examples

### Baseline example with no override

This uses normal runtime resolution because no explicit user override is being
supplied.

```python
revealed_df = reveal_dataframe(
    spark.table(TARGET_TABLE),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)
```

Example `helper_options`:

```python
helper_options = {
    "api_version": effective_api_version,
    "transport_mode": effective_transport_mode,
    "spark_group_size": effective_spark_group_size,
    "batch_size": tuning_resolution.effective_crdp_request_item_target,
    "v2_max_items_per_request": effective_v2_max_items,
    "v2_max_policy_groups_per_request": effective_v2_max_policy_groups,
    "v2_enable_multi_policy": effective_v2_enable_multi_policy,
}
```

### Explicit reveal-user override when allowed

```python
revealed_df = reveal_dataframe(
    spark.table(TARGET_TABLE),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
    reveal_user="svc_databricks_batch",
)
```

If:

```properties
REVEAL_USER_OVERRIDE_ALLOWED=true
```

then the helper can honor `svc_databricks_batch`.

### Override by Spark SQL expression when allowed

```python
helper_options = {
    "api_version": effective_api_version,
    "transport_mode": effective_transport_mode,
    "spark_group_size": effective_spark_group_size,
    "batch_size": tuning_resolution.effective_crdp_request_item_target,
    "v2_max_items_per_request": effective_v2_max_items,
    "v2_max_policy_groups_per_request": effective_v2_max_policy_groups,
    "v2_enable_multi_policy": effective_v2_enable_multi_policy,
    "reveal_user_expr": "'svc_databricks_batch'",
}

revealed_df = reveal_dataframe(
    spark.table(TARGET_TABLE),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
)
```

If:

```properties
REVEAL_USER_OVERRIDE_ALLOWED=true
```

then the helper can resolve reveal user from `reveal_user_expr`.

### What happens when the flag blocks the override

If the config contains:

```properties
REVEAL_USER_OVERRIDE_ALLOWED=false
```

then this explicit override:

```python
revealed_df = reveal_dataframe(
    spark.table(TARGET_TABLE),
    object_name=PROTECTED_OBJECT_NAME,
    config=config,
    options=helper_options,
    reveal_user="svc_databricks_batch",
)
```

is ignored by the helper.

Likewise this option:

```python
"reveal_user_expr": "'svc_databricks_batch'"
```

is also ignored when overrides are disabled.

## Unity Catalog Python wheel API examples

### Protect example: not affected by the flag

```python
token = uc_protect_by_object_and_column(
    value="alice@example.com",
    object_name="my_catalog.my_schema.customer_protected",
    column_name="email",
    config_path="/tmp/thales_config/udfConfig.properties",
    transport_mode="real",
)
```

This call is a protect operation, so `REVEAL_USER_OVERRIDE_ALLOWED` does not
apply.

### Reveal example: affected by the flag

```python
plaintext = uc_reveal_by_object_and_column(
    value=token,
    object_name="my_catalog.my_schema.customer_protected",
    column_name="email",
    config_path="/tmp/thales_config/udfConfig.properties",
    reveal_user="svc_batch_user",
    transport_mode="real",
)
```

If:

```properties
REVEAL_USER_OVERRIDE_ALLOWED=true
```

then `svc_batch_user` may be honored.

If:

```properties
REVEAL_USER_OVERRIDE_ALLOWED=false
```

then the override is blocked and the helper uses its locked reveal-user
behavior.

### Bulk reveal example

```python
values = uc_reveal_bulk_by_object_and_column(
    values=["token1", "token2"],
    object_name="my_catalog.my_schema.customer_protected",
    column_name="email",
    config_path="/tmp/thales_config/udfConfig.properties",
    reveal_user="svc_batch_user",
    transport_mode="real",
)
```

This is also governed by `REVEAL_USER_OVERRIDE_ALLOWED` because it is a reveal
API.

## How to verify what happened

For the DataFrame helper path, the easiest way is to inspect the generated plan
summary:

```python
print(revealed_df._thales_bulk_plan_summary)
```

The most useful fields are:

- `resolved_reveal_user`
- `reveal_user_resolution`
- `reveal_user_override_allowed`

These help confirm whether an override was accepted or ignored.

## Recommended usage

### Development or test

```properties
REVEAL_USER_OVERRIDE_ALLOWED=true
```

This is useful when testing service-account patterns or controlled reveal-user
behavior.

### Production or governed use

```properties
REVEAL_USER_OVERRIDE_ALLOWED=false
```

This is the safer setting when reveal should remain tightly tied to platform
runtime identity behavior.

## Bottom line

- The flag applies to **Python helper reveal APIs**.
- It does **not** apply to protect APIs.
- For Unity Catalog-oriented Python wheel functions, it matters on:
  - `uc_reveal_by_object_and_column(...)`
  - `uc_reveal_bulk_by_object_and_column(...)`
  - related row and rowset reveal helpers
- It does **not** matter on:
  - `uc_protect_by_object_and_column(...)`
  - other protect-only UC helper functions
