# Conversation Engine

Persistent state machine.

## Initial States
START, MENU, SERVICE, STAFF, DATE, SLOT, CONFIRMATION, COMPLETED, CANCELLED, HUMAN_HANDOFF.

## Rules
- Explicit transitions.
- Recoverable unexpected responses.
- Configurable timeout.
- Safe restart.
- Minimal temporary context.
- Final confirmation before booking.
