from django.db import models


class DailyMetrics(models.Model):
    id = models.AutoField(primary_key=True)
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="daily_metrics",
    )
    date = models.DateField()
    total_appointments = models.PositiveIntegerField(default=0)
    confirmed_appointments = models.PositiveIntegerField(default=0)
    cancelled_appointments = models.PositiveIntegerField(default=0)
    completed_appointments = models.PositiveIntegerField(default=0)
    no_show_appointments = models.PositiveIntegerField(default=0)
    new_customers = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    messages_received = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "analytics_daily_metrics"
        unique_together = ["business", "date"]
        ordering = ["-date"]
