# Business Rules

1. Every operational entity belongs to a business.
2. No user can access information from another business.
3. An appointment cannot overlap with another for the same professional.
4. The professional must be enabled for the service.
5. The duration of the appointment comes from the service at the time of booking.
6. The booking must respect schedules, exceptions, and blocks.
7. Canceling or rescheduling must record the actor, date, and reason.
8. Duplicate webhooks must not duplicate operations.
9. All dates are persisted in UTC and presented in the business's timezone.
10. Plan limits are validated on the backend.
