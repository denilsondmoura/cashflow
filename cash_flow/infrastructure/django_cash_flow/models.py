from django.db import models


class PlanningModel(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50)
    end_date = models.DateField()
    average_daily_expenditure = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_balance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    updated_at = models.DateField(auto_now=True)
    status = models.CharField(max_length=50, default="active")

    class Meta:
        db_table = '"cash_flow"."plannings"'


class BudgetModel(models.Model):
    planning = models.ForeignKey(PlanningModel, related_name='budgets', on_delete=models.CASCADE)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    limit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = '"cash_flow"."budgets"'


class TransactionModel(models.Model):
    planning = models.ForeignKey(PlanningModel, related_name='transactions', on_delete=models.CASCADE)
    due_date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=20)  # inflow/outflow
    cleared = models.BooleanField(default=False)
    cleared_at = models.DateField(null=True, blank=True)
    auto_pay = models.BooleanField(default=False)

    class Meta:
        db_table = '"cash_flow"."transactions"'


class NotificationModel(models.Model):
    planning = models.ForeignKey(PlanningModel, related_name='notifications', on_delete=models.CASCADE)
    trigger_date = models.DateField()
    message = models.TextField()
    related_transaction = models.ForeignKey(TransactionModel, null=True, blank=True, on_delete=models.SET_NULL)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = '"cash_flow"."notifications"'
