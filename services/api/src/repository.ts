import sql from 'mssql';

export type Role = 'user' | 'admin';

export interface Principal {
  tenantId: string;
  objectId: string;
}

export interface Membership {
  organizationId: string;
  role: Role;
}

export interface SocketTicketIdentity extends Principal {
  organizationId: string;
  role: Role;
}

export interface AuthRepository {
  membershipsFor(principal: Principal): Promise<Membership[]>;
  membershipFor(principal: Principal, organizationId: string): Promise<Membership | undefined>;
  createSocketTicket(ticketHash: string, principal: Principal, organizationId: string, expiresAt: Date): Promise<boolean>;
  consumeSocketTicket(ticketHash: string, organizationId: string, now: Date): Promise<SocketTicketIdentity | undefined>;
  close?(): Promise<void>;
}

export interface SqlConnectionSettings {
  server: string;
  database: string;
  managedIdentityClientId?: string;
}

export class RetryableConnection<T> {
  private pending: Promise<T> | undefined;

  get(connect: () => Promise<T>): Promise<T> {
    if (this.pending) return this.pending;
    const attempt = connect();
    this.pending = attempt;
    void attempt.catch(() => {
      if (this.pending === attempt) this.pending = undefined;
    });
    return attempt;
  }

  get hasAttempt(): boolean {
    return this.pending !== undefined;
  }
}

export class SqlAuthRepository implements AuthRepository {
  private readonly pool: sql.ConnectionPool;
  private readonly connected = new RetryableConnection<sql.ConnectionPool>();

  constructor(settings: SqlConnectionSettings) {
    this.pool = new sql.ConnectionPool({
      server: settings.server,
      database: settings.database,
      options: { encrypt: true, trustServerCertificate: false },
      authentication: {
        type: 'azure-active-directory-default',
        options: settings.managedIdentityClientId
          ? { clientId: settings.managedIdentityClientId }
          : {},
      },
    });
  }

  private connection(): Promise<sql.ConnectionPool> {
    return this.connected.get(() => this.pool.connect());
  }

  async membershipsFor(principal: Principal): Promise<Membership[]> {
    const pool = await this.connection();
    const result = await pool.request()
      .input('tenantId', sql.UniqueIdentifier, principal.tenantId)
      .input('objectId', sql.UniqueIdentifier, principal.objectId)
      .query<{ organizationId: string; role: Role }>(`
        SELECT OrganizationId AS organizationId, Role AS role
        FROM dbo.OrganizationMembership
        WHERE TenantId = @tenantId AND ObjectId = @objectId AND IsActive = 1
      `);
    return result.recordset;
  }

  async membershipFor(principal: Principal, organizationId: string): Promise<Membership | undefined> {
    const pool = await this.connection();
    const result = await pool.request()
      .input('tenantId', sql.UniqueIdentifier, principal.tenantId)
      .input('objectId', sql.UniqueIdentifier, principal.objectId)
      .input('organizationId', sql.UniqueIdentifier, organizationId)
      .query<{ organizationId: string; role: Role }>(`
        SELECT OrganizationId AS organizationId, Role AS role
        FROM dbo.OrganizationMembership
        WHERE TenantId = @tenantId AND ObjectId = @objectId
          AND OrganizationId = @organizationId AND IsActive = 1
      `);
    return result.recordset[0];
  }

  async createSocketTicket(
    ticketHash: string,
    principal: Principal,
    organizationId: string,
    expiresAt: Date,
  ): Promise<boolean> {
    const pool = await this.connection();
    const result = await pool.request()
      .input('ticketHash', sql.Char(64), ticketHash)
      .input('tenantId', sql.UniqueIdentifier, principal.tenantId)
      .input('objectId', sql.UniqueIdentifier, principal.objectId)
      .input('organizationId', sql.UniqueIdentifier, organizationId)
      .input('expiresAt', sql.DateTime2, expiresAt)
      .query(`
        DELETE FROM dbo.WebSocketTicket
        WHERE ExpiresAt <= SYSUTCDATETIME()
          OR (ConsumedAt IS NOT NULL AND ConsumedAt < DATEADD(hour, -1, SYSUTCDATETIME()));

        INSERT INTO dbo.WebSocketTicket (TicketHash, TenantId, ObjectId, OrganizationId, ExpiresAt)
        OUTPUT inserted.TicketHash AS ticketHash
        SELECT @ticketHash, @tenantId, @objectId, @organizationId, @expiresAt
        WHERE EXISTS (
          SELECT 1 FROM dbo.OrganizationMembership
          WHERE TenantId = @tenantId AND ObjectId = @objectId
            AND OrganizationId = @organizationId AND IsActive = 1
        )
      `);
    return result.recordset.length === 1;
  }

  async consumeSocketTicket(
    ticketHash: string,
    organizationId: string,
    now: Date,
  ): Promise<SocketTicketIdentity | undefined> {
    const pool = await this.connection();
    const result = await pool.request()
      .input('ticketHash', sql.Char(64), ticketHash)
      .input('organizationId', sql.UniqueIdentifier, organizationId)
      .input('now', sql.DateTime2, now)
      .query<SocketTicketIdentity>(`
        UPDATE ticket
        SET ConsumedAt = @now
        OUTPUT inserted.TenantId AS tenantId, inserted.ObjectId AS objectId,
          inserted.OrganizationId AS organizationId, membership.Role AS role
        FROM dbo.WebSocketTicket AS ticket
        INNER JOIN dbo.OrganizationMembership AS membership
          ON membership.TenantId = ticket.TenantId
          AND membership.ObjectId = ticket.ObjectId
          AND membership.OrganizationId = ticket.OrganizationId
          AND membership.IsActive = 1
        WHERE ticket.TicketHash = @ticketHash
          AND ticket.OrganizationId = @organizationId
          AND ticket.ConsumedAt IS NULL
          AND ticket.ExpiresAt > @now
      `);
    return result.recordset[0];
  }

  async close(): Promise<void> {
    if (this.connected.hasAttempt) await this.pool.close();
  }
}

export class MemoryAuthRepository implements AuthRepository {
  private readonly memberships = new Map<string, Role>();
  private readonly tickets = new Map<string, SocketTicketIdentity & { expiresAt: Date; consumed: boolean }>();

  addMembership(principal: Principal, organizationId: string, role: Role): void {
    this.memberships.set(this.membershipKey(principal, organizationId), role);
  }

  revokeMembership(principal: Principal, organizationId: string): void {
    this.memberships.delete(this.membershipKey(principal, organizationId));
  }

  private membershipKey(principal: Principal, organizationId: string): string {
    return `${principal.tenantId.toLowerCase()}:${principal.objectId.toLowerCase()}:${organizationId.toLowerCase()}`;
  }

  async membershipsFor(principal: Principal): Promise<Membership[]> {
    const prefix = `${principal.tenantId.toLowerCase()}:${principal.objectId.toLowerCase()}:`;
    return [...this.memberships.entries()]
      .filter(([key]) => key.startsWith(prefix))
      .map(([key, role]) => ({ organizationId: key.slice(prefix.length), role }));
  }

  async membershipFor(principal: Principal, organizationId: string): Promise<Membership | undefined> {
    const role = this.memberships.get(this.membershipKey(principal, organizationId));
    return role ? { organizationId, role } : undefined;
  }

  async createSocketTicket(
    ticketHash: string,
    principal: Principal,
    organizationId: string,
    expiresAt: Date,
  ): Promise<boolean> {
    const membership = await this.membershipFor(principal, organizationId);
    if (!membership) return false;
    this.tickets.set(ticketHash, { ...principal, ...membership, expiresAt, consumed: false });
    return true;
  }

  async consumeSocketTicket(
    ticketHash: string,
    organizationId: string,
    now: Date,
  ): Promise<SocketTicketIdentity | undefined> {
    const ticket = this.tickets.get(ticketHash);
    if (!ticket || ticket.consumed || ticket.expiresAt <= now || ticket.organizationId.toLowerCase() !== organizationId.toLowerCase()) {
      return undefined;
    }
    const membership = await this.membershipFor(ticket, organizationId);
    ticket.consumed = true;
    if (!membership) return undefined;
    return { tenantId: ticket.tenantId, objectId: ticket.objectId, organizationId, role: membership.role };
  }
}
