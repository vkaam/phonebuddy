-- Least-privilege access for the API runtime identity. The identity itself is
-- environment specific, so the release adds it to this role; nothing here names
-- a principal. Idempotent: safe to run on every release.
IF DATABASE_PRINCIPAL_ID(N'pb_api') IS NULL
  CREATE ROLE pb_api;

GRANT SELECT ON OBJECT::dbo.OrganizationMembership TO pb_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::dbo.WebSocketTicket TO pb_api;

-- The API never writes memberships: they are seeded and changed only by the
-- release step and the database administrator.
REVOKE INSERT, UPDATE, DELETE ON OBJECT::dbo.OrganizationMembership FROM pb_api;
