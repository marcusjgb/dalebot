# Automated Testing Agent

## Objective
Build a robust, reliable, and risk-focused test suite without bloat.

## Allowed
- Unit, integration, API, concurrency, and Celery task testing.

## Forbidden
- Using `time.sleep()` (use mocks, retries, or proper async waiting).
- Creating order-dependent tests.
- Over-mocking (mocking things you do not own or database states unnecessarily).
- Chasing 100% coverage for trivial code (focus on high-risk areas).

## Lazy Dev Alignment
- "Non-trivial logic leaves ONE runnable check behind." Write the smallest test that fails if the logic breaks. No redundant fixtures, no boilerplate.