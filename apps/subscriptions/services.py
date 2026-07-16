from django.db import transaction
from django.utils import timezone


@transaction.atomic
def create_subscription(business, plan="free"):
    from .models import PlanType, Subscription, SubscriptionStatus

    if Subscription.objects.filter(business=business).exists():
        raise ValueError("Business already has a subscription")

    plan_type = (
        plan.lower()
        if isinstance(plan, str)
        else plan.value if hasattr(plan, "value")
        else plan
    )
    if plan_type not in [p[0] for p in PlanType.choices]:
        raise ValueError(f"Invalid plan: {plan}")

    subscription = Subscription.objects.create(
        business=business,
        plan=plan_type,
        status=SubscriptionStatus.ACTIVE,
    )

    _log_subscription_created(subscription)

    return subscription


@transaction.atomic
def upgrade_subscription(subscription, new_plan):
    from apps.audit.services import log_action

    from .models import PlanType

    if new_plan not in [p[0] for p in PlanType.choices]:
        raise ValueError(f"Invalid plan: {new_plan}")

    old_plan = subscription.plan
    subscription.plan = new_plan.lower() if isinstance(new_plan, str) else new_plan
    subscription.save()

    log_action(
        user=None,
        business=subscription.business,
        action="upgrade_plan",
        entity_type="Subscription",
        entity_id=subscription.id,
        changes={"old_plan": old_plan, "new_plan": new_plan},
    )

    return subscription


@transaction.atomic
def cancel_subscription(subscription):
    from apps.audit.services import log_action

    from .models import SubscriptionStatus

    subscription.status = SubscriptionStatus.CANCELLED
    subscription.ends_at = timezone.now()
    subscription.save()

    log_action(
        user=None,
        business=subscription.business,
        action="cancel_subscription",
        entity_type="Subscription",
        entity_id=subscription.id,
        changes={"plan": subscription.plan},
    )

    return subscription


def _log_subscription_created(subscription):
    from apps.audit.services import log_action
    log_action(
        user=None,
        business=subscription.business,
        action="create_subscription",
        entity_type="Subscription",
        entity_id=subscription.id,
        changes={"plan": subscription.plan},
    )
