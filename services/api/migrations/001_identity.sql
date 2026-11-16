IF OBJECT_ID(N'dbo.OrganizationMembership', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.OrganizationMembership (
    OrganizationId uniqueidentifier NOT NULL,
    TenantId uniqueidentifier NOT NULL,
    ObjectId uniqueidentifier NOT NULL,
    Role nvarchar(16) NOT NULL,
    IsActive bit NOT NULL CONSTRAINT DF_OrganizationMembership_IsActive DEFAULT (1),
    CreatedAt datetime2(3) NOT NULL CONSTRAINT DF_OrganizationMembership_CreatedAt DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT PK_OrganizationMembership PRIMARY KEY (OrganizationId, TenantId, ObjectId),
    CONSTRAINT CK_OrganizationMembership_Role CHECK (Role IN (N'user', N'admin'))
  );
  CREATE INDEX IX_OrganizationMembership_Principal
    ON dbo.OrganizationMembership (TenantId, ObjectId, IsActive)
    INCLUDE (OrganizationId, Role);
END;

IF OBJECT_ID(N'dbo.WebSocketTicket', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.WebSocketTicket (
    TicketHash char(64) NOT NULL,
    TenantId uniqueidentifier NOT NULL,
    ObjectId uniqueidentifier NOT NULL,
    OrganizationId uniqueidentifier NOT NULL,
    ExpiresAt datetime2(3) NOT NULL,
    ConsumedAt datetime2(3) NULL,
    CreatedAt datetime2(3) NOT NULL CONSTRAINT DF_WebSocketTicket_CreatedAt DEFAULT (SYSUTCDATETIME()),
    CONSTRAINT PK_WebSocketTicket PRIMARY KEY (TicketHash),
    CONSTRAINT FK_WebSocketTicket_Membership FOREIGN KEY (OrganizationId, TenantId, ObjectId)
      REFERENCES dbo.OrganizationMembership (OrganizationId, TenantId, ObjectId)
  );
  CREATE INDEX IX_WebSocketTicket_Expiration ON dbo.WebSocketTicket (ExpiresAt, ConsumedAt);
END;
