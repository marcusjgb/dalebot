# Backend

## Structure per Module
- `models.py`: persistence.
- `services.py`: writes and use cases.
- `selectors.py`: complex queries.
- `schemas.py`: API contracts.
- `api.py`: HTTP transport.
- `tasks.py`: asynchronous tasks.
- `exceptions.py`: domain errors.
- `tests/`: tests.

## Rules
- `transaction.atomic()` in critical operations.
- `select_for_update()` under concurrency.
- External side effects after commit.
- Public services with docstring.
- Typing where it improves comprehension.
