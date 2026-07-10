# Profile Resolution Order

This note explains how the current Java UDF path and Python helper path resolve
protection profiles from `udfConfig.properties`.

## Resolution Order

Profile resolution is performed per column, not as an all-or-nothing lookup for
 the whole object.

For each column, the resolver checks these sources in order:

1. `protect.object.<object_name>`
2. `column.<column_name>.profile`
3. `COLUMN_PROFILES`
4. `protection_profile`

This means:

- object-specific mappings win for columns they explicitly define
- if a column is missing from the object-specific mapping, resolution continues
- the existence of a `protect.object...` entry does not block fallback for
  missing columns

## Example Configuration

```properties
protect.object.my_catalog.my_schema.plaintext_protected_internal=address|tag.char.internal,ssn|tag.nbr.internal,creditcard|tag.nbr.internal,creditcardcode|tag.nbr.internal

column.email.profile=tag.char.internal

COLUMN_PROFILES=email|tag.char.none,address|tag.char.none,ssn|tag.nbr.none

protection_profile=alpha-external
```

## Example Result

Assume code is resolving columns against:

```text
my_catalog.my_schema.plaintext_protected_internal
```

Then the effective results are:

| Column | Resolution source | Result |
| --- | --- | --- |
| `address` | `protect.object...` | `tag.char.internal` |
| `ssn` | `protect.object...` | `tag.nbr.internal` |
| `creditcard` | `protect.object...` | `tag.nbr.internal` |
| `email` | `column.email.profile` | `tag.char.internal` |
| `city` | `protection_profile` | `alpha-external` |

## Practical Interpretation

Example: `address`

- found in `protect.object.my_catalog.my_schema.plaintext_protected_internal`
- resolver stops there

Example: `email`

- not found in the object-specific entry
- next checks `column.email.profile`
- finds `tag.char.internal`
- resolver stops there

Example: `ssn`

- found in the object-specific entry
- even if `COLUMN_PROFILES` also contains `ssn`, the object-specific mapping
  still wins

Example: `city`

- not found in `protect.object...`
- no `column.city.profile`
- not found in `COLUMN_PROFILES`
- falls back to `protection_profile`

## Mental Model

Use this mental model when explaining the behavior:

- object-specific override first
- explicit per-column override second
- shared column mapping third
- global default last

## Low-Level Java UDF Interpretation

For Java object-aware UDFs such as:

```sql
thales_protect_by_object_and_column(
  mysensitive_data,
  'char',
  'my_catalog.my_schema.plaintext_protected_internal',
  'email'
)
```

the arguments are interpreted as:

1. value to protect
2. datatype hint
3. object lookup key
4. column lookup key

Important clarification:

- the 3rd argument is not itself a profile name
- the 3rd argument does not need to match a real `protect.object...` entry
- if `protect.object.<3rd-arg>` does not exist, the resolver can still fall
  back to `column.<4th-arg>.profile`, then `COLUMN_PROFILES`, then
  `protection_profile`

This means a Java developer can use a placeholder object name for an ad hoc
test, as long as the column name still resolves through one of the fallback
layers.

## Python Helper Interpretation

For the Python helper API:

```python
protected_df = protect_dataframe(
    df=source_df,
    object_name="my_catalog.my_schema.plaintext_protected_internal",
    config=config,
    options=helper_options,
)
```

`object_name` is also treated as an object lookup key, not as a profile name.

Important clarification:

- `object_name` does not need to exist in `protect.object...`
- but the helper still needs discoverable sensitive columns
- in practice, helper auto-discovery works best when columns are defined in
  either `protect.object...`, `column.<name>.profile`, or `COLUMN_PROFILES`

So the Python helper path is more sensitive than the low-level Java path to how
columns are modeled in the config.

## Ad Hoc Development Use Cases

### One-Off Java Test Without Editing Object Mappings

A developer can run a low-level Java UDF call with a placeholder object name:

```sql
thales_protect_by_object_and_column(
  mysensitive_data,
  'char',
  'my_catalog.my_schema.plaintext_protected_internal_arrays_not_found',
  'sam_char'
)
```

If this object mapping does not exist, the resolver will continue to:

1. `column.sam_char.profile`
2. `COLUMN_PROFILES` entry for `sam_char`
3. `protection_profile`

This works well for quick targeted SQL or Java UDF experiments.

### One-Off Python Helper Test

For Python helper tests, the recommended pattern is to define the test columns
through `column.<name>.profile` or `COLUMN_PROFILES`, then let the helper use
those columns naturally from the DataFrame schema.

This is more reliable than expecting `protection_profile` alone to drive helper
selection, because `protection_profile` is a last-resort profile fallback, not
the primary helper column-discovery mechanism.

## Team and Developer Testing Patterns

The design supports lightweight testing conventions where teams reserve certain
column names for shared testing and individuals reserve others for personal
experiments.

Example:

```properties
column.team_char.profile=tag.teamchar.none
column.team_nbr.profile=tag.teamnbr.none

column.sam_char.profile=tag.samchar.none
column.sam_nbr.profile=tag.samnbr.none
```

This lets:

- the team use `team_char` and `team_nbr` in shared examples and demos
- Sam use `sam_char` and `sam_nbr` in personal tests without changing the
  shared object mappings

This pattern is especially useful when:

- developers want quick repeatable smoke tests
- teams want shared scratch-profile conventions
- the same environment supports both common team tests and individual testing

## Recommended Development Practice

For development and experimentation:

- use `column.<name>.profile` for quick, explicit, low-friction testing
- use reserved team test names for shared examples
- use personal reserved names only for short-lived or clearly understood
  development scenarios
- keep `protection_profile` as a last-resort fallback, not as the primary
  design for repeatable helper jobs

## Recommended Production Practice

For production, the model should be locked down and clearly governed.

Recommended production rules:

- keep the chosen profile model in source control
- treat profile changes as change-managed configuration updates
- avoid ad hoc personal profile names in production environments
- use a clearly documented primary model so operators and developers know what
  to expect

The two main production models are:

1. global column-oriented model using `column.<name>.profile`
2. object-specific model using `protect.object.<object_name>`

Both are supported, but the organization should be deliberate about which model
is primary.

Good production guidance is:

- use `column.<name>.profile` when the same business column should resolve the
  same way across many jobs
- use `protect.object.<object_name>` when specific protected objects need to
  override the broader column default
- document the intended use of fallback so teams understand why two columns with
  the same name may or may not resolve the same way in different objects

## Flexibility Versus Clarity

The design is intentionally flexible, but it must be clearly understood.

If multiple hierarchy layers are implemented at the same time:

- the behavior is deterministic
- but it is easy for teams to become confused if they do not know which layer
  is expected to be authoritative

The best practice is:

- keep the hierarchy small when possible
- document which layer is intended to win in the normal case
- use diagnostics to verify effective resolution during rollout and testing
- avoid mixing too many temporary testing conventions into production configs

## Config Version Metadata Best Practice

Organizations should also version the effective `udfConfig.properties` state so
runtime diagnostics clearly show which configuration baseline was active during
execution.

Recommended metadata block:

```properties
CONFIG_VERSION=2026.06.12.1
CONFIG_RELEASE_DATE=2026-06-12
CONFIG_CHANGE_REF=customer-demo-baseline
CONFIG_NOTES=Short one-line summary of the environment-specific config state.
```

These fields are intended to be lightweight runtime fingerprints, not a
replacement for proper source-control history.

Recommended meaning:

- `CONFIG_VERSION`: the config revision identifier used by the organization
- `CONFIG_RELEASE_DATE`: the date that revision was published or promoted
- `CONFIG_CHANGE_REF`: a release label, Git tag, work item, or other reference
- `CONFIG_NOTES`: a short one-line summary of the active environment state

## Version-Control Guidance

Best practice is to treat `udfConfig.properties` as governed configuration, not
as an informal scratch file.

Recommended practice:

- store production config in source control
- update `CONFIG_VERSION` whenever the effective runtime behavior changes
- update `CONFIG_CHANGE_REF` to point to the relevant release, tag, or work
  item
- keep `CONFIG_NOTES` short and operational
- keep detailed rationale and historical change descriptions in Git history,
  release notes, or tickets

Avoid turning the properties file itself into a long-form changelog.

## Promotion Guidance

When promoting config across environments such as dev, test, and production:

- increment `CONFIG_VERSION`
- update `CONFIG_RELEASE_DATE`
- update `CONFIG_CHANGE_REF` to the deployment or release reference
- keep the promoted file aligned with the committed source-controlled version

This makes runtime diagnostics much more useful because a notebook run or smoke
test can immediately show:

- which config baseline ran
- when it was published
- which release or change record it came from

## Development Versus Production

For development:

- temporary experimentation is fine
- `CONFIG_NOTES` can briefly describe what is being tested
- individual test profiles may be acceptable in shared non-production
  environments

For production:

- the config should be treated as controlled configuration
- profile naming and fallback behavior should be intentional and documented
- the metadata block should match the exact file promoted through source
  control
- the detailed explanation of what changed should live in source control, not
  inside the properties file

## Applies To

This resolution order now applies consistently to:

- Java object-aware UDF profile resolution
- Python helper API profile resolution
