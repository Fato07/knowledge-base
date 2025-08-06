---
title: Solitude Project
permalink: solitude-project
tags:
  - project
  - ai-agents
  - marketplace
  - golang
  - react
---

# Solitude Project

## Observations

### Project Overview
- [description] AI Agent marketplace where buyers hire and manage AI employees
- [business_model] Sellers build AI agents with UI interfaces and host them on marketplace
- [vision] Building the future of work through AI agent automation
- [stage] Active development with staging environment at staging.app.solitude.ai

### Technical Architecture
- [backend] Go service handling API business logic for orchestrating AI agents
- [frontend] React Remix with Vite, ShadCN, and Tailwind CSS
- [architecture] Agents bundled into workspaces with specific tasks and UI interaction modes
- [deployment] Cloud Run on Google Cloud, with future AWS and Fly.io expansion

### Database Layer
- [primary_db] PostgreSQL for business structures and relational data
- [document_db] MongoDB for document metadata storage
- [graph_db] Memgraph for agent memory management
- [vector_db] Weaviate for vector embeddings and similarity search
- [schema] Complex ER diagram with 40+ tables managing users, businesses, workspaces, workflows

### Infrastructure Stack
- [auth] WorkOS for SSO and directory sync
- [workflow] Temporal for workflow orchestration
- [iac] Terraform and Pulumi for infrastructure as code
- [secrets] Infisical for customer secrets, Google Cloud Secrets for infrastructure
- [observability] Honeycomb.io for monitoring and tracing

### Development Workflow
- [local_testing] Use `/backend/compose.local.yaml` with CREATE_TEST_DATA=true
- [test_credentials] User: test@solitude.ai, Password: password123
- [staging] Merge to staging branch deploys to staging.app.solitude.ai
- [git_workflow] Feature branches → staging → production

### Key Entities
- [entity] Business - Companies using the platform
- [entity] Users - Individual users within businesses
- [entity] Sellers - AI agent creators
- [entity] Workspaces - Container for AI agents with specific tasks
- [entity] Workflows - Orchestrated sequences of activities
- [entity] Jobs - Execution instances of workflows
- [entity] Teams - Organizational units within businesses

### Security & Access Control
- [rbac] Role-based access control with admin/viewer/none permissions
- [api_auth] API keys for seller authentication
- [token_mgmt] Refresh token system with expiration tracking
- [sso] WorkOS integration for enterprise SSO

### File Management
- [storage] File directory system with bucket-based storage
- [tracking] File access history for audit trails
- [association] Files linked to jobs and users

### GPU Infrastructure
- [compute] GPU cluster management for AI workloads
- [ownership] User-owned clusters with status tracking
- [scaling] Configurable GPUs per node

## Relations

- uses [[Go Backend]]
- implements [[React Remix Frontend]]
- manages [[AI Agents]]
- stores_in [[PostgreSQL]]
- stores_in [[MongoDB]]
- stores_in [[Memgraph]]
- stores_in [[Weaviate]]
- orchestrates_with [[Temporal]]
- authenticates_with [[WorkOS]]
- deploys_to [[Google Cloud Run]]
- monitors_with [[Honeycomb]]
- developed_with [[Claude Code Setup]]
- architecture_in [[Solitude Architecture]]
- logged_in [[Solitude Development Log]]
- tested_with [[Docker Compose]]
- secured_with [[JWT Authentication]]
- follows [[Microservices Architecture]]
- tracked_in [[Git Repository]]

## Resources

- [repository] ~/DEV/MyProjects/solitude
- [staging] http://staging.app.solitude.ai
- [local] compose.local.yaml for local development

## Next Steps

- [todo] Set up local development environment
- [todo] Document API endpoints
- [todo] Create workflow examples
- [todo] Test agent creation flow
- [todo] Review security configurations
