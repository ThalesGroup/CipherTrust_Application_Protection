# Thales UserSet Sync Tool

Standalone utility for synchronizing CipherTrust Manager user sets from LDAP, Active Directory, Microsoft Entra, Okta, or SCIM 2.0 sources, either from exported files or direct live connections.

## What It Does

- lists existing CipherTrust user sets
- creates missing user sets
- reconciles user set membership to match source files exactly
- can query live LDAP / Active Directory / Microsoft Entra sources
- can query live Okta group membership
- can query generic SCIM 2.0 group membership
- writes audit snapshots for review and rollback
- restores a user set from a saved snapshot file

## Main Class

- `com.thales.usersets.tool.IdentityUserSetSyncTool`

## Build

```powershell
mvn clean -DskipTests package
```

## Output Artifact

- `target/thales-userset-sync-tool-0.0.1-SNAPSHOT-all.jar`

## Config File

Start from:

- `identity-userset-sync.properties`

## Source Modes

- `FILE`
  - reads one exported file per OU or group
- `LIVE`
  - queries the source system directly
  - LDAP / AD uses JNDI LDAP search
  - Entra uses Microsoft Graph with application credentials
  - Okta uses the Okta Groups API with an API token
  - SCIM uses standard SCIM 2.0 group endpoints with a bearer token

## Modes

- `CHECK`
  - lists existing CipherTrust user sets and planned target user sets
- `SYNC`
  - creates missing user sets and reconciles membership
- `ROLLBACK`
  - restores one user set from a saved audit snapshot

## Source Models

- LDAP
  - one input file per OU
  - user set name format: `baseDn-OU`
  - live mode can search a direct OU without traversing child OUs
- Active Directory
  - in this tool, on-prem AD uses the same live LDAP connector pattern as LDAP
- Entra / Active Directory
  - one input file per logical group
  - user set name format: `prefix-group`
  - live Entra mode reads members from Microsoft Graph group membership
- Okta
  - one input file per logical group in file mode
  - user set name format: `prefix-group`
  - live Okta mode reads group members from the Okta Groups API
- SCIM
  - one input file per logical group in file mode
  - user set name format: `prefix-group`
  - live SCIM mode reads group members from SCIM 2.0 group resources

## Audit And Safety

- `audit.dir`
  - writes `current`, `desired`, `add`, and `remove` snapshots
- `sync.maxRemovals`
  - absolute delete guard
- `sync.maxRemovalPercent`
  - percentage delete guard

## Secure LDAP / AD Options

- `ldap.transportSecurity`
  - `NONE`
  - `SSL`
  - `STARTTLS`
- `ldap.connectTimeoutMillis`
  - LDAP connect timeout
- `ldap.readTimeoutMillis`
  - LDAP read timeout
- `ldap.excludeDisabledUsers`
  - when `true`, skips disabled accounts in AD-style directories
- `ldap.disabledStatusAttribute`
  - defaults to `userAccountControl`

All three transport modes are supported by the tool:

- `NONE`
  - plain LDAP
  - no transport encryption
  - does not require truststore settings
- `SSL`
  - LDAPS
  - encrypted from the start
  - usually uses port `636`
  - requires the JVM to trust the LDAP server certificate
- `STARTTLS`
  - connects over standard LDAP and upgrades to TLS
  - often uses port `389`
  - requires the JVM to trust the LDAP server certificate

Important:

- `NONE` is still valid and supported
- `NONE` may still be rejected by your LDAP / AD server if the directory requires secure binds
- for production, prefer `SSL` or `STARTTLS`

## Truststore-Friendly Wrappers

The wrapper scripts now support these environment variables so you do not have to type JVM truststore flags each run:

- `JAVA_TRUSTSTORE_PATH`
- `JAVA_TRUSTSTORE_PASSWORD`
- `JAVA_TRUSTSTORE_TYPE`

These map to the standard JVM SSL properties:

- `javax.net.ssl.trustStore`
- `javax.net.ssl.trustStorePassword`
- `javax.net.ssl.trustStoreType`

Typical values:

- `JAVA_TRUSTSTORE_TYPE=JKS`
- `JAVA_TRUSTSTORE_TYPE=PKCS12`

These truststore variables are only needed for `ldap.transportSecurity=SSL` or `ldap.transportSecurity=STARTTLS`.
They are not needed for `ldap.transportSecurity=NONE`.

## Windows Examples

Preview:

```powershell
.\run-identity-userset-sync.bat .\identity-userset-sync.properties > .\identity-check.txt
```

Scheduled run:

```powershell
powershell -ExecutionPolicy Bypass -File .\schedule-identity-userset-sync.ps1 -ConfigFile .\identity-userset-sync.properties
```

With truststore variables:

```powershell
$env:JAVA_TRUSTSTORE_PATH="E:\certs\corp-truststore.jks"
$env:JAVA_TRUSTSTORE_PASSWORD="changeit"
$env:JAVA_TRUSTSTORE_TYPE="JKS"
powershell -ExecutionPolicy Bypass -File .\schedule-identity-userset-sync.ps1 -ConfigFile .\identity-userset-sync-check-live.properties
```

Live LDAP example properties:

```properties
source.mode=LIVE
source.type=LDAP
ldap.transportSecurity=SSL
ldap.url=ldaps://ldap.example.com:636
ldap.bindDn=cn=syncuser,ou=service,dc=example,dc=com
ldap.password=changeme
ldap.baseDn=dc=example,dc=com
ldap.ous=HR,Finance
ldap.userIdAttribute=userPrincipalName
ldap.searchFilter=(objectClass=person)
ldap.subtree=false
ldap.excludeDisabledUsers=true
```

Plain LDAP example properties:

```properties
source.mode=LIVE
source.type=LDAP
ldap.transportSecurity=NONE
ldap.url=ldap://ldap.example.com:389
ldap.bindDn=cn=syncuser,ou=service,dc=example,dc=com
ldap.password=changeme
ldap.baseDn=dc=example,dc=com
ldap.ous=HR
ldap.userIdAttribute=userPrincipalName
ldap.searchFilter=(objectClass=person)
ldap.subtree=false
ldap.excludeDisabledUsers=true
```

Use the plain LDAP example only if your directory permits unencrypted binds and your environment accepts that risk.

Live Entra example properties:

```properties
source.mode=LIVE
source.type=ENTRA
entra.tenantId=<tenant-id>
entra.clientId=<client-id>
entra.clientSecret=<client-secret>
entra.namespaces=HR
entra.prefix.HR=hrdepartment
entra.groups.HR=alloweduser,maskeduser
entra.groupId.HR.alloweduser=<group-guid>
entra.groupId.HR.maskeduser=<group-guid>
```

Live Okta example properties:

```properties
source.mode=LIVE
source.type=OKTA
okta.baseUrl=https://company.okta.com
okta.apiToken=<api-token>
okta.namespaces=HR
okta.prefix.HR=hrdepartment
okta.groups.HR=alloweduser,maskeduser
okta.groupId.HR.alloweduser=<group-id>
okta.groupId.HR.maskeduser=<group-id>
okta.userIdAttribute=profile.login
okta.activeUsersOnly=true
```

Live SCIM example properties:

```properties
source.mode=LIVE
source.type=SCIM
scim.baseUrl=https://example.com/scim/v2
scim.bearerToken=<bearer-token>
scim.namespaces=HR
scim.prefix.HR=hrdepartment
scim.groups.HR=alloweduser,maskeduser
scim.groupId.HR.alloweduser=<group-id>
scim.groupId.HR.maskeduser=<group-id>
scim.userIdAttribute=display
scim.pageSize=100
```

## Linux Examples

Preview:

```bash
./run-identity-userset-sync.sh ./identity-userset-sync.properties > ./identity-check.txt
```

Scheduled run:

```bash
./schedule-identity-userset-sync.sh ./identity-userset-sync.properties
```

With truststore variables:

```bash
export JAVA_TRUSTSTORE_PATH=/opt/certs/corp-truststore.jks
export JAVA_TRUSTSTORE_PASSWORD=changeit
export JAVA_TRUSTSTORE_TYPE=JKS
./schedule-identity-userset-sync.sh ./identity-userset-sync-check-live.properties
```

## Ready-To-Run Live Check Profile

Start with:

- `identity-userset-sync-check-live.properties`

This sample is already configured with:

- `sync.mode=CHECK`
- `source.mode=LIVE`
- secure LDAP transport placeholders
- disabled-user filtering enabled

That makes it the safest first validation step before you enable `SYNC`.

## Rollback

Set these properties before running:

```properties
sync.mode=ROLLBACK
rollback.userSetName=dc=example,dc=com-HR
rollback.snapshot.phase=presync
rollback.snapshot.type=current
```

Or point directly at a saved file:

```properties
rollback.snapshot.file=E:/eclipse-workspace/thales-userset-sync-tool/audit/identity-userset-sync/dc_example_dc_com-HR/presync-current.txt
```

## Entra Permissions

For Entra live mode, the app registration typically needs Microsoft Graph application permissions sufficient to read group membership, such as `GroupMember.Read.All`. If you also choose to resolve groups dynamically in the future, `Group.Read.All` is commonly used as well.

## Okta Permissions

For Okta live mode, the token or OAuth client needs permission to read groups and group members. In Okta's Groups API, listing group members is done through the group users endpoint.

## SCIM Notes

This first-pass SCIM implementation is intentionally practical rather than universal.

It supports:

- bearer-token authentication
- group lookup by ID
- optional fallback lookup by group display name
- standard SCIM list pagination fields
- configurable member identifier mapping

Because SCIM providers vary in how they populate group member details, you may need to adjust `scim.userIdAttribute` for your environment. The default implementation currently works best when the SCIM provider returns useful `members[].display` values.
