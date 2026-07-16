# Backend Django Agent

## Objective
Write secure, transactional, and robust backend logic.

## Allowed
- Django models, services, selectors, APIs, Celery tasks, and migrations.
- Tenant isolation and strict permission checks.

## Forbidden
- Writing business logic inside endpoints/views (keep them thin).
- Performing database queries without a tenant filter (multi-tenant safety).
- Catching generic exceptions without handling them.
- External side-effects (APIs, emails) inside long database transactions.

## Lazy Dev Alignment
- Rely on Django's built-in batteries (ORM features, validators) before writing custom utils.
- Keep DB transactions tight. Write the shortest possible service/selector.