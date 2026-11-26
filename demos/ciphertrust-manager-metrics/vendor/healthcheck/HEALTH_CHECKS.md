# Health Checks Reference

This document lists every check performed by [`run_healthcheck.py`](run_healthcheck.py) (`analyze_health`), grouped by report section. Severity levels: **FAIL**, **WARNING**, **INFO**.

## Licensing

- [ ] Flag any license in `expired` state — **FAIL**
- [ ] Flag any license past its expiration date — **FAIL**
- [ ] Flag any license expiring within 30 days — **WARNING**
- [ ] Flag any trial license with 30 or fewer days of `trial_seconds_remaining` — **WARNING** (trial license expiration is displayed as days derived from `trial_seconds_remaining`, since the `expiration` field is always `"no expiration"` on a live trial countdown)
- [ ] Flag any licensed feature in `expired` status — **FAIL**
- [ ] Flag any licensed feature with 30 or fewer days of `trial_seconds_remaining` — **WARNING** (feature expiration is derived from `trial_seconds_remaining`, converted to days, since the `expiration` field is always `"no expiration"` even for features on a live trial countdown)
- [ ] Report a license expiration value that could not be parsed, instead of silently ignoring it — **INFO**
- [ ] Report whether an active trial mode is enabled — **INFO**

## System & Cluster

- [ ] Verify NTP is synchronized (`ntpq -p` shows a `*` peer, no timeout/error) — **WARNING** if not synced
- [ ] Flag disk encryption `attendedBoot` enabled (requires manual passphrase at boot) — **WARNING**
- [ ] Verify a pre-authentication login banner is configured — **WARNING** if missing
- [ ] Verify a scheduled database backup job exists and is enabled — **WARNING** if missing
- [ ] Verify at least one backup exists — **WARNING** if none
- [ ] Flag latest backup older than 7 days — **WARNING**
- [ ] Flag backups referencing a backup key ID that no longer exists — **FAIL**
- [ ] Flag backups referencing a backup key that is not `active` — **WARNING**
- [ ] Flag any backup key not in `active` state — **WARNING**
- [ ] Flag cluster errors when the node is clustered — **FAIL**
- [ ] Flag active, unacknowledged alarms — **FAIL** if any are critical/emergency/alert/error severity, otherwise **WARNING**
- [ ] Flag system properties that differ from their documented default value — **INFO**
- [ ] Flag Root-of-Trust keys older than 365 days — **WARNING**
- [ ] Report disabled scheduler configurations — **INFO**
- [ ] Verify overall system services status is `started` — **WARNING** if not
- [ ] Flag any individual system service not in `started` state — **WARNING**
- [ ] Verify at least one NTP server is configured — **WARNING** if none
- [ ] Verify an SMTP server is configured for email alerting — **WARNING** if none
- [ ] Verify notification email recipients are set when an SMTP server is configured — **WARNING** if none
- [ ] Report whether an outbound proxy is configured — metric only
- [ ] Report total licensed feature count — metric only
- [ ] Verify the Prometheus metrics API is enabled — **WARNING** if disabled

## Access Control

- [ ] Flag locked-out user accounts (`account_lockout_at` set) — **WARNING**
- [ ] Flag user accounts that have never logged in — **WARNING**
- [ ] Flag user accounts inactive for more than 30 days — **WARNING**
- [ ] Flag user accounts with `login_flags.login_flags == true` — **WARNING**
- [ ] Flag user accounts with failed login attempts (and not currently locked out) — **WARNING**
- [ ] Report custom (non-`global`) password policies — metric only
- [ ] Flag password policies with a minimum length under 8 characters — **WARNING**
- [ ] Flag password policies with password reuse prevention disabled (`history == 0`) — **WARNING**
- [ ] Flag password policies with account lockout disabled (empty lockout thresholds) — **WARNING**
- [ ] Report password policies with no password expiration enforced (`pwdchngdays == 0`) — **INFO**
- [ ] Flag `admin` group members who have never logged in — **WARNING**
- [ ] Report `admin` group members who have logged in — **INFO**
- [ ] Report count of active quorum policies — metric only
- [ ] Report custom (non-system) security groups — metric only
- [ ] Flag `ldaps://` LDAP connections with certificate verification disabled (`insecure_skip_verify == true`) — **FAIL**
- [ ] Flag `ldaps://` LDAP connections with no `root_ca` configured (relies on OS trust store) — **WARNING**

## Domains

- [ ] Report domains with `allow_user_management` enabled — **INFO**
- [ ] Flag domains backed by an HSM connection (reports connection ID and KEK label) — **WARNING**

## Network

- [ ] Flag disabled service interfaces — **WARNING**
- [ ] Flag service interfaces using an insecure/anonymous auth mode (`no-tls-pw-opt`, `no-tls-pw-req`, `unauth-tls-pw-opt`, `unauth-tls-pw-req`) — **FAIL**
- [ ] Flag service interfaces with a weak minimum TLS version (SSLv3, TLS 1.0, TLS 1.1) — **FAIL**
- [ ] Flag enabled service interfaces with no Post-Quantum Cryptography key exchange group enabled — **WARNING**
- [ ] Verify at least one active external log forwarder is configured — **FAIL** if none
- [ ] List each interface's trusted local/external CAs, certificate user field, and local auto-gen attributes (CN, Organization) — display only

## Keys

- [ ] Collapse key versions and flag any key whose highest version is not in `Active` state — **WARNING**
- [ ] Flag weak key configurations: RSA < 2048 bits, AES < 128 bits — **FAIL**
- [ ] Report key counts by type, state, and label — metrics only
- [ ] Flag deleted domains with orphaned keys left behind (`ksctl reports orphaned-resources`) — **WARNING**

## Certificate Authorities

- [ ] Flag expired trusted CA certificates — **FAIL**
- [ ] Flag trusted CA certificates expiring within 30 days — **WARNING**
- [ ] Flag expired local CAs — **FAIL**
- [ ] Flag local CAs expiring within 30 days — **WARNING**
- [ ] Flag expired external CAs — **FAIL**
- [ ] Flag external CAs expiring within 30 days — **WARNING**

## Transparent Encryption (CTE)

- [ ] Flag CTE clients whose `client_health_status` is not `Healthy` — **WARNING**
- [ ] Flag CTE GuardPoints not in `ACTIVE` state — **WARNING**
- [ ] Flag CTE policies with Learn Mode enabled (`never_deny == true`) — **WARNING**
- [ ] Report total CTE clients/policies and key/subdomain capacity usage — metrics only

## Clients

- [ ] Report total and active registered client counts — metrics only
- [ ] List active clients (Name, ID, Connector, IP/Hostname, Created At, State) in the report — display only

## Event Records

- [ ] Review server audit records (`ksctl records list`) from the last 7 days; flag `error` — **WARNING**; flag `critical`/`fatal` — **FAIL**
- [ ] Review client audit records (`ksctl client-records list`) from the last 7 days; flag `error` — **WARNING**; flag `critical`/`fatal` — **FAIL**
- [ ] `info`/`warning`/`debug` severity records are not flagged; server and client records are tracked and displayed separately
- [ ] Report total reviewed vs. significant (above-Info) event counts for both server and client records — metrics only

## Overall Status

- [ ] Aggregate all section statuses: overall is **FAIL** if any section is FAIL, else **WARNING** if any section is WARNING, else **PASS**
