---
title: Database Patterns and Best Practices
permalink: database-patterns-and-best-practices
tags:
  - solitude
  - 2025-08-06
---

# Database Patterns and Best Practices

## Observations

- [created] Note created from Claude Code at 2025-08-06 15:18:00
- [project] Working on solitude at /Users/fathindosunmu/DEV/MyProjects/solitude

## Relations

- part_of [[solitude]]

## Content

### Multi-Database Design Patterns

#### 1. Polyglot Persistence Pattern
**Implementation**: Solitude uses specialized databases for different data characteristics
- **PostgreSQL**: ACID transactions, complex queries, structured data
- **MongoDB**: Flexible schemas, rapid iteration, document storage  
- **Temporal DB**: Workflow state management, distributed processing

**Benefits**:
- Optimal performance for each data type
- Technology-specific optimizations
- Independent scaling strategies

#### 2. Database-per-Service Pattern
**Implementation**: Each major service domain has isolated data access
- **User Service**: PostgreSQL for profiles, authentication, workspaces
- **Activity Service**: MongoDB for metadata, execution context
- **Workflow Service**: Temporal database for orchestration state

**Benefits**:
- Service autonomy and loose coupling
- Independent deployment and scaling
- Technology choice flexibility per domain

### Connection Management Patterns

#### 1. Connection Pool Pattern
**PostgreSQL Implementation**:
```go
// pgxpool.Pool with optimal configuration
cfg.ConnConfig.Tracer = otelpgx.NewTracer()
conn, err := pgxpool.NewWithConfig(ctx, cfg)
```

**Benefits**:
- Efficient resource utilization
- Reduced connection overhead
- Built-in health monitoring

#### 2. Single Client Pattern  
**MongoDB Implementation**:
```go
// Reuse single mongo.Client across operations
client, err := mongo.Connect(ctx, options.Client().ApplyURI(cfg.URI))
```

**Benefits**:
- Reduced connection latency
- Simplified configuration management
- Better resource predictability

### Data Access Patterns

#### 1. Repository Pattern with SQLC
**Implementation**: Type-safe SQL with generated Go code
```yaml
# sqlc.yaml configuration
queries: "./queries.sql"
schema: "./migrations"  
engine: "postgresql"
```

**Benefits**:
- Compile-time query validation
- Type safety without ORM complexity
- Performance of hand-written SQL

#### 2. Dynamic Collection Pattern
**MongoDB Implementation**: Collections per workspace/job
```go
collection := fmt.Sprintf("%s/%s", workspaceID, jobID)
userAgents := client.Database(metadataDB).Collection(collection)
```

**Benefits**:
- Tenant isolation at database level
- Scalable partitioning strategy
- Flexible schema evolution per workspace

### Transaction Management Patterns

#### 1. Explicit Transaction Pattern
**PostgreSQL Implementation**:
```go
tx, err := pool.Begin(ctx)
defer tx.Rollback(ctx) // Always defer rollback
// ... perform operations
tx.Commit(ctx) // Explicit commit on success
```

**Benefits**:
- Clear transaction boundaries
- Proper error handling and cleanup
- ACID compliance for critical operations

#### 2. Context-Aware Operations Pattern
**MongoDB Implementation**:
```go
ctx, span := tracer.Start(ctx, "AddMetadata")
defer span.End()
_, err := collection.InsertOne(ctx, document)
```

**Benefits**:
- Timeout and cancellation support
- Distributed tracing integration
- Graceful error handling

### Observability Patterns

#### 1. Distributed Tracing Pattern
**Implementation**: OpenTelemetry across all databases
```go
// PostgreSQL tracing
cfg.ConnConfig.Tracer = otelpgx.NewTracer()

// MongoDB tracing  
ctx, span := tracer.Start(ctx, operationName)
defer span.End()
```

**Benefits**:
- End-to-end request visibility
- Performance bottleneck identification
- Cross-service correlation

#### 2. Health Check Pattern
**Docker Compose Implementation**:
```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "admin", "-d", "test"]
  interval: 5s
  timeout: 5s
  retries: 5
```

**Benefits**:
- Automated failure detection
- Service dependency management
- Graceful degradation capabilities

### Security Patterns

#### 1. Credential Isolation Pattern
**Implementation**: Environment-based configuration
```go
type PostgresConfig struct {
    User     string `validate:"required"`
    Password string // Optional for key-based auth
    Host     string `validate:"required"`
}
```

**Benefits**:
- Secrets management separation
- Environment-specific configuration
- Reduced credential exposure

#### 2. Database User Isolation Pattern
**Implementation**: Separate users for different services
- `admin` user for application data (PostgreSQL)
- `temporal` user for workflow data (PostgreSQL 12)
- Service-specific MongoDB authentication

**Benefits**:
- Principle of least privilege
- Blast radius limitation
- Audit trail clarity

### Performance Optimization Patterns

#### 1. UUID Primary Key Pattern
**Implementation**: UUID-based primary keys for distributed scalability
```go
// SQLC override for UUID handling
overrides:
- db_type: "uuid"
  go_type:
    import: "github.com/google/uuid"
    type: "UUID"
```

**Benefits**:
- Distributed ID generation
- No central ID bottleneck
- Merge-friendly for distributed systems

#### 2. Prepared Statement Pattern
**Implementation**: SQLC-generated prepared queries
```yaml
gen:
  go:
    emit_prepared_queries: true
    emit_json_tags: true
```

**Benefits**:
- Query plan caching
- SQL injection prevention
- Consistent performance

### Anti-Patterns to Avoid

#### 1. ❌ Cross-Database Transactions
**Problem**: ACID transactions across PostgreSQL and MongoDB
**Solution**: Use saga pattern or event-driven consistency

#### 2. ❌ Shared Connection Pools
**Problem**: Single pool for multiple services
**Solution**: Service-isolated connection management

#### 3. ❌ Generic Repository Pattern
**Problem**: One-size-fits-all data access
**Solution**: Database-specific access patterns

#### 4. ❌ Synchronous Cross-Database Operations
**Problem**: Blocking calls between databases
**Solution**: Event-driven async patterns

### Best Practices Summary

#### Configuration
- Environment-based database configuration
- Validation at application startup
- Health checks for all database connections

#### Development
- Schema-first approach with migrations
- Type-safe query generation (SQLC)
- Comprehensive error handling

#### Operations  
- Distributed tracing for observability
- Connection pooling for efficiency
- Proper transaction boundaries

#### Security
- Credential isolation and rotation
- Database user separation
- Audit logging for compliance

### Related Documentation

- [[Database Architecture]] - Overall database design
- [[Solitude Architecture]] - System architecture context
- [[Performance Monitoring]] - Database performance tracking
- [[Security Patterns]] - Database security implementation

