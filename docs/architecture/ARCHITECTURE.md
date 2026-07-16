# Architecture

## Style
Modular monolith deployed as a single application, divided by domains with explicit boundaries.

## Rationale
- Lower operating cost.
- Simple local development.
- Consistent transactions.
- Fewer distributed failures.
- Better velocity for a small team.
- Ability to extract modules when evidence exists.

## Rules
- Endpoints translate transport; they do not implement rules.
- Writes live in `services.py`.
- Complex reads live in `selectors.py`.
- WhatsApp integration calls public domain services.
- No module accesses the internal details of another.
- Circular dependencies are forbidden.
- Internal events are used only when they decouple a real need.
