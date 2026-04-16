-- Unity Catalog grant examples for SQL Warehouse secured reveal views
--
-- Recommended model:
-- - end users get USE CATALOG, USE SCHEMA, and SELECT on secured views
-- - end users do not get EXECUTE on the underlying *_with_user functions
-- - administrators or deployment principals create the functions and views
--
-- Example principals:
-- - `pii_consumers` is the end-user or BI-reader group
-- - `thales_udf_deployers` is the deployment/admin group

-- Optional: grant discovery and navigation privileges for the consumer group.
GRANT USE CATALOG ON CATALOG main TO `pii_consumers`;
GRANT USE SCHEMA ON SCHEMA main.security TO `pii_consumers`;

-- Grant read access only to the secured views.
GRANT SELECT ON VIEW main.security.v_customer_reveal TO `pii_consumers`;
GRANT SELECT ON VIEW main.security.v_employee_reveal TO `pii_consumers`;
GRANT SELECT ON VIEW main.security.v_customer_array_reveal TO `pii_consumers`;

-- Optional: if you want broad read access to all current and future views in
-- the schema, you can grant SELECT at the schema level.
-- Use this only if the schema contains only approved reveal views.
--
-- GRANT SELECT ON SCHEMA main.security TO `pii_consumers`;

-- Deployment/admin principal grants.
GRANT USE CATALOG ON CATALOG main TO `thales_udf_deployers`;
GRANT USE SCHEMA ON SCHEMA main.security TO `thales_udf_deployers`;
GRANT USE SCHEMA ON SCHEMA main.raw TO `thales_udf_deployers`;

-- Allow deployers to create functions and views in the target schema.
GRANT CREATE FUNCTION ON SCHEMA main.security TO `thales_udf_deployers`;
GRANT CREATE TABLE ON SCHEMA main.security TO `thales_udf_deployers`;

-- Allow deployers/view owners to read source tables referenced by the views.
GRANT SELECT ON TABLE main.raw.customer_tokens TO `thales_udf_deployers`;
GRANT SELECT ON TABLE main.raw.employee_tokens TO `thales_udf_deployers`;
GRANT SELECT ON TABLE main.raw.customer_token_arrays TO `thales_udf_deployers`;

-- Allow deployers to execute the UC functions during validation and view
-- creation. End users do not need these direct function grants when you want
-- the views to be the only supported access path.
GRANT EXECUTE ON FUNCTION main.security.thales_crdp_scalar_by_column_with_user TO `thales_udf_deployers`;
GRANT EXECUTE ON FUNCTION main.security.thales_crdp_bulk_by_column_with_user TO `thales_udf_deployers`;

-- Validation:
-- SHOW GRANTS ON VIEW main.security.v_customer_reveal;
-- SHOW GRANTS ON FUNCTION main.security.thales_crdp_scalar_by_column_with_user;
