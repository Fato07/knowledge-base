---
title: Database Architecture
permalink: database-architecture
tags:
  - solitude
  - 2025-08-06
---

# Database Architecture

## Observations

- [created] Note created from Claude Code at 2025-08-06 15:13:08
- [project] Working on solitude at /Users/fathindosunmu/DEV/MyProjects/solitude

## Relations

- part_of [[solitude]]

## Content

### Overview

The Solitude project implements a **multi-database polyglot persistence strategy** with specialized databases for different data types and use cases. This architecture supports the AI Agent marketplace platform with optimized data storage patterns.

### Database Stack

#### Primary Databases

**PostgreSQL (Main Relational Store)**
- **Version**: PostgreSQL 16
- **Port**: 5432 (main), 5433 (temporal)
- **Purpose**: Core business logic, structured data, transactional operations
- **ORM/Query Builder**: SQLC for type-safe SQL generation
- **Connection**: pgx/v5 with connection pooling via pgxpool
- **Observability**: OpenTelemetry tracing with otelpgx

**Stored Data Types**:
- Business entities, user management, workspace data
- Audit logs, file metadata, dataset management
- Tool definitions, approval workflows, invitations
- Activity schemas and structured configurations

**MongoDB (Document Store)**
- **Version**: Latest MongoDB
- **Port**: 27017
- **Purpose**: Flexible document storage, metadata, semi-structured data
- **Collections**: Dynamic collections per workspace/job (`{workspaceID}/{jobID}`)

**Stored Data Types**:
- Activity metadata (unstructured activity instance data)
- Integration data (Microsoft Outlook, external APIs)
- Job execution metadata and runtime context

**PostgreSQL 12 (Temporal Dedicated)**
- **Version**: PostgreSQL 12, **Port**: 5433
- **Purpose**: Dedicated database for Temporal workflow engine
- **Isolation**: Separate instance to avoid resource contention

### Architecture Patterns

#### Data Distribution Strategy

| Data Type | Database | Rationale |
|-----------|----------|-----------|
| **Business entities** | PostgreSQL | ACID compliance, referential integrity |
| **User profiles** | PostgreSQL | Strong consistency, authentication |
| **Audit logs** | PostgreSQL | Immutable audit trail, compliance |
| **Tool definitions** | PostgreSQL | Structured configuration, validation |
| **Activity metadata** | MongoDB | Flexible schema, rapid ingestion |
| **Integration data** | MongoDB | Semi-structured external responses |
| **Workflow state** | Temporal DB | Specialized workflow requirements |

#### Connection Management

**PostgreSQL**:
- Connection pooling via pgxpool.Pool
- Transaction support with explicit rollback
- OpenTelemetry tracing integration
- Type-safe queries via SQLC

**MongoDB**:
- Single mongo.Client with connection reuse
- Context-aware operations for cancellation
- Dynamic database/collection selection

### Performance & Monitoring

#### Optimizations
- **PostgreSQL**: Connection pooling, prepared statements, UUID indexing
- **MongoDB**: Single client reuse, workspace isolation via collections
- **Temporal**: Dedicated database instance, health check monitoring

#### Observability
- **Tracing**: OpenTelemetry integration across all databases
- **Health Checks**: Automated monitoring with 5s intervals
- **Metrics**: Performance tracking for all operations

### Security & Configuration

#### Access Control
- Database-level user isolation (admin/temporal separation)
- Environment-based configuration with validation
- Encrypted connections and credential management

#### Development Setup
- Docker Compose orchestration with service dependencies
- Automated key generation and health monitoring
- Persistent volumes for data retention

### Related Architecture

- [[Solitude Architecture]] - Overall system design
- [[Temporal Workflows]] - Workflow orchestration
- [[API Design]] - Database-API integration
- [[Development Environment]] - Local setup

