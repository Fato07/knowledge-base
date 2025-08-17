# OpenTelemetry Implementation in Solitude

#architecture #observability #opentelemetry #honeycomb #distributed-tracing

## Overview

Solitude implements end-to-end distributed tracing using OpenTelemetry from frontend to backend, with Honeycomb as the visualization and analysis platform. This document captures the current implementation state and identified improvements.

## Frontend Implementation

### Configuration
- **Location**: `frontend/app/lib/observability.client.ts`
- **SDK**: Honeycomb Web SDK with OpenTelemetry auto-instrumentation
- **Service Name**: `solitude-frontend`
- **Dataset**: `solitude-unified`
- **Endpoint**: `https://api.eu1.honeycomb.io:443`

### Key Features
```typescript
// Initialization before React hydration
initializeObservability();

// Auto-instrumentation includes:
- Fetch requests with CORS propagation
- XMLHttpRequest tracking
- User interaction events
- Resource attributes for service identification
```

### Trace Propagation
```javascript
propagateTraceHeaderCorsUrls: [
  /^http:\/\/localhost:3000/,
  /^https:\/\/api\.solitude\.ai/,
  /^https:\/\/staging\.api\.solitude\.ai/
]
```

## Backend Implementation

### Configuration
- **Location**: `backend/internal/tracer/tracer.go`
- **Protocol**: OTLP gRPC
- **Service Name**: `solitude-backend` (instance ID)
- **Dataset**: `solitude-unified` (used as service.name)

### Components

#### HTTP Middleware
```go
// Extracts trace context from headers
propagator.Extract(r.Context(), propagation.HeaderCarrier(r.Header))

// Creates server span with HTTP attributes
tracer.Start(ctx, fmt.Sprintf("%s %s", r.Method, r.URL.Path))
```

#### Database Tracing

**PostgreSQL** (`backend/internal/storage/postgres/postgres.go`):
```go
cfg.ConnConfig.Tracer = otelpgx.NewTracer()
```

**MongoDB** (`backend/internal/storage/mongo/metadata.go`):
```go
ctx, span := tracer.Start(ctx, "OperationName")
defer span.End()
```

#### Temporal Workflow Tracing
```go
// backend/internal/tracer/workflow.go
opentelemetry.NewTracingInterceptor(opentelemetry.TracerOptions{Tracer: tracer})
```

## Request Flow

1. **Browser** → User action triggers instrumented request
2. **Frontend** → Adds trace headers (traceparent, tracestate, baggage)
3. **Backend** → Middleware extracts context, creates linked span
4. **Database** → Operations create child spans
5. **Honeycomb** → All spans sent to unified dataset

## Environment Configuration

### Frontend (.env)
```bash
VITE_HONEYCOMB_API_KEY="your_api_key"
VITE_HONEYCOMB_SERVICE_NAME="solitude-frontend"
VITE_HONEYCOMB_ENDPOINT="https://api.eu1.honeycomb.io:443"
VITE_HONEYCOMB_DATASET="solitude-unified"
```

### Backend (.env)
```bash
SERVICE_NAME=solitude-backend
OTEL_EXPORTER_OTLP_ENDPOINT=your_endpoint
OTEL_COLLECTOR_TOKEN=your_token
HONEYCOMB_DATASET=solitude-unified
```

## Current Issues & Improvements

### 1. Inconsistent Service Naming
- **Issue**: Backend uses dataset as service name, original name as instance ID
- **Impact**: Confusing queries in Honeycomb
- **Solution**: Standardize naming convention across services

### 2. Missing Trace Sampling
- **Issue**: `AlwaysSample()` expensive at scale
- **Impact**: High costs, performance overhead
- **Solution**: Implement tail-based sampling

### 3. Limited Custom Spans
- **Issue**: Business logic lacks instrumentation
- **Impact**: Missing visibility into critical operations
- **Solution**: Add spans for key business operations

### 4. No Metrics Collection
- **Issue**: Only traces, no metrics
- **Impact**: Can't track SLIs effectively
- **Solution**: Add OpenTelemetry metrics

### 5. Error Handling
- **Issue**: Silent failures in frontend, warnings in backend
- **Impact**: Tracing gaps go unnoticed
- **Solution**: Better error reporting and monitoring

### 6. Security Considerations
- **Issue**: Trace headers in CORS configuration
- **Impact**: Potential information leakage
- **Solution**: Review security implications

## Related Documentation

- [[Database Architecture]] - Database tracing details
- [[Solitude Architecture]] - System overview
- [[Database Patterns and Best Practices]] - Observability patterns

## Implementation Timeline

- **Current Branch**: `feature/open-telementary-setup`
- **Status**: Active development
- **Next Steps**: Address identified improvements

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Honeycomb Documentation](https://docs.honeycomb.io/)
- [OTLP Specification](https://opentelemetry.io/docs/reference/specification/protocol/otlp/)