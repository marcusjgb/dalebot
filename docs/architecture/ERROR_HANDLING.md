# Error Handling

## Categories
- Domain.
- Validation.
- Authorization.
- Integration.
- Infrastructure.
- Retryable.
- Non-retryable.

## Rules
- Do not catch `Exception` without handling.
- Do not expose stack traces.
- Use correlation ID.
- Clear messages for the user and technical details in logs.
- Retries with backoff and limit.
- Dead-letter strategy for persistent failures.
