---
title: Solitude Datasets and Invoice Processing
permalink: solitude-datasets
tags:
  - solitude
  - datasets
  - invoice-processing
  - approval-workflow
  - 2025-08-07
---

# Solitude Datasets and Invoice Processing

## Observations

- [created] Note created from Claude Code at 2025-08-07 10:45:00
- [project] Working on solitude at /Users/fathindosunmu/DEV/MyProjects/solitude
- [context] Dataset management and invoice extraction workflow

## Dataset Architecture

### Core Entities

**Dataset Entry (DatasetEntry)**
- [purpose] Container for processed data from AI activities
- [storage] PostgreSQL for metadata, MongoDB for flexible document data
- [key_fields] 
  - `dataset_row.analysis_result` - JSON result from AI processing
  - `dataset_row.ground_truth` - Validated/corrected data
  - `identifiers.job_id` - Links to workflow job
  - `identifiers.approval_ids` - Links to approval workflow

**Invoice Processing Flow**
1. [extraction] AI agent extracts invoice data (supplier, PO number, total, currency)
2. [storage] Results stored as dataset entries with analysis_result JSON
3. [approval] Pending invoices require human approval/rejection
4. [status] Tracks as: extracting → pending → approved/rejected

### Invoice State Management

**Key Components**:
- [hook] `useInvoiceState` - Unified state manager for invoice operations
- [persistence] Filter preferences saved to localStorage per workspace
- [real-time] Polling every 10s for extraction updates, 60s for stable data

**Invoice Data Model**:
```typescript
Invoice {
  id: string
  status: "extracting" | "pending" | "approved" | "rejected"
  supplierName: string | null
  poNumber: string | null  
  totalAmount: string
  currency: string | null
  audit: Audit // Source audit entry
  dataset?: DatasetEntry // Extracted data
  approvalId?: string // For approval actions
}
```

### API Endpoints

**Dataset Operations**:
- `GET /business/{id}/workspaces/{wid}/datasets` - List datasets with cursor pagination
- `GET /business/{id}/workspaces/{wid}/datasets/{did}` - Get specific dataset
- `POST /business/{id}/workspaces/{wid}/datasets/{did}/human-annotation` - Update annotations

**Approval Workflow**:
- `GET /business/{id}/workspaces/{wid}/approval` - List workspace approvals
- `PATCH /business/{id}/workspaces/{wid}/approval/{aid}` - Approve/reject with annotations

### Performance Optimizations

- [caching] Query results cached with 5s stale time for snappy UI
- [polling] Smart polling - faster (10s) when pending items exist
- [batching] Approval status mapped in bulk to avoid N+1 queries
- [memoization] Heavy computations memoized with useMemo

### Security Considerations

- [auth] All API calls require business context and authentication
- [rbac] Approval actions restricted based on user permissions
- [audit] All approval actions tracked in audit logs

## Relations

- part_of [[solitude]]
- uses [[database-architecture]]
- implements [[approval-workflow]]
- stores_in [[PostgreSQL]]
- stores_in [[MongoDB]]

## Technical Details

### State Atoms (Jotai)
- `AuditsAtom` - Global audit entries
- `SelectedAuditAtom` - Currently selected audit/invoice
- `approveJobActivityMutationAtom` - Approval mutation handler

### Hooks Architecture
- `useDatasets` - Fetches dataset list with pagination
- `useWorkspaceApprovals` - Fetches approval statuses
- `useApproveJobActivity` - Handles approve/reject mutations
- `useAuditEntriesAtom` - Fetches audit entries

### Error Handling
- Toast notifications for user-facing errors
- Automatic query invalidation on mutations
- Graceful handling of missing data relationships

## Common Issues & Solutions

1. **Missing Approvals**
   - Ensure approval IDs are properly linked in dataset identifiers
   - Check workflow configuration includes approval steps

2. **Stale Data**
   - Queries auto-refresh based on polling intervals
   - Manual refresh available via `actions.refresh()`

3. **Performance**
   - Large invoice lists filtered client-side for responsive UI
   - Consider server-side filtering for >1000 invoices

## Future Enhancements

- [todo] Server-side search and filtering
- [todo] Bulk approval operations
- [todo] Export functionality for processed invoices
- [todo] Advanced analytics on approval patterns