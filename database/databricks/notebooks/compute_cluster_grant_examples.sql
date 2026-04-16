-- Compute-cluster grant examples
-- SAMPLE ONLY:
-- - these are patterns for persistent catalog/schema objects
-- - they do not apply directly to TEMP VIEWs created in a notebook session
--
-- Important:
-- - TEMP VIEWs are session-scoped and are not the usual target for durable
--   grants
-- - if you want governed shared access, create persistent Unity Catalog views
--   such as main.security.v_customer_reveal and grant SELECT on those views
-- - Java session UDF registrations themselves are not Unity Catalog functions,
--   so there is no UC EXECUTE privilege to grant for them

-- Recommended consumer grants for persistent views created from cluster SQL:
GRANT USE CATALOG ON CATALOG main TO `pii_consumers`;
GRANT USE SCHEMA ON SCHEMA main.security TO `pii_consumers`;
GRANT SELECT ON VIEW main.security.v_customer_reveal TO `pii_consumers`;
GRANT SELECT ON VIEW main.security.v_employee_reveal TO `pii_consumers`;
GRANT SELECT ON VIEW main.security.v_customer_array_reveal TO `pii_consumers`;

-- Example grants for the numeric-measure sample tables:
GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_plaintext TO `thales_cluster_deployers`;
GRANT SELECT ON TABLE my_catalog.my_schema.account_balance_tokens TO `thales_cluster_deployers`;

-- Deployment/admin grants for the team creating the views from the cluster:
GRANT USE CATALOG ON CATALOG main TO `thales_cluster_deployers`;
GRANT USE SCHEMA ON SCHEMA main.security TO `thales_cluster_deployers`;
GRANT USE SCHEMA ON SCHEMA main.raw TO `thales_cluster_deployers`;
GRANT CREATE TABLE ON SCHEMA main.security TO `thales_cluster_deployers`;
GRANT SELECT ON TABLE main.raw.customer_tokens TO `thales_cluster_deployers`;
GRANT SELECT ON TABLE main.raw.employee_tokens TO `thales_cluster_deployers`;
GRANT SELECT ON TABLE main.raw.customer_token_arrays TO `thales_cluster_deployers`;

-- If you are only using TEMP VIEWs for notebook validation, SQL GRANT
-- statements are typically unnecessary because TEMP VIEWs live only inside the
-- active session and are not shared durable objects.
