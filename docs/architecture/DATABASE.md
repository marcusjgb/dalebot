# Database

## Engine
PostgreSQL.

## Multi-tenancy
Shared model with mandatory `business_id` on operational entities.

## Conventions
- UUID for public identifiers.
- UTC for timestamps.
- Constraints in database and application.
- Composite indexes by business when appropriate.
- Soft delete for auditable entities.
- JSONB only for variable data or external payloads.
- Backward-compatible migrations when possible.

## Principal Risk
Leakage between tenants. Every query and permission must be validated by business.
