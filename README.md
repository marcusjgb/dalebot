# WhatsApp Appointments

Multi-company SaaS to book, cancel, and reschedule appointments via WhatsApp.

## Status

Initial repository for architecture, documentation, agents, and skills. Productive code must be developed in phases following `docs/product/ROADMAP.md`.

## Stack

- Python
- Django
- Django Ninja
- PostgreSQL
- Redis
- Celery
- Django Templates
- HTMX
- Tailwind CSS
- Docker Compose
- Nginx
- Pytest
- GitHub Actions
- Meta WhatsApp Cloud API

## Principles

- Modular monolith
- KISS
- DRY with judgment
- YAGNI
- Security by default
- Strict multi-tenancy
- Business logic outside of views and endpoints
- Risk-centered testing
- Documentation synchronized with code

## Intended Start

1. Copy `.env.example` to `.env`.
2. Implement the Django bootstrap.
3. Spin up PostgreSQL and Redis with Docker Compose.
4. Create the user and business models.
5. Follow the roadmap in phases.

## Order of Authority

1. PRD
2. Business rules
3. Architecture
4. Security
5. ADR
6. Coding standards
7. Implementation
