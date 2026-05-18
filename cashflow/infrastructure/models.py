from django.db import models
from django.utils import timezone
from auth.infrastructure.models import Profile

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Profile, null=True, blank=True, related_name='created_%(class)s', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(Profile, null=True, blank=True, related_name='updated_%(class)s', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class PlanningModel(BaseModel):
    name = models.CharField(max_length=255)
    end_date = models.DateField()
    start_billing_cycle = models.IntegerField(default=1)
    average_daily_expenditure = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_balance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, default="updated")
    users = models.ManyToManyField(Profile, related_name='plannings')

    class Meta:
        db_table = '"cashflow"."plannings"'


class BudgetModel(BaseModel):
    planning = models.ForeignKey(PlanningModel, related_name='budgets', on_delete=models.CASCADE)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    limit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = '"cashflow"."budgets"'


class TransactionModel(BaseModel):
    planning = models.ForeignKey(PlanningModel, related_name='transactions', on_delete=models.CASCADE)
    due_date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=20)  # inflow/outflow
    cleared = models.BooleanField(default=False)
    cleared_at = models.DateField(null=True, blank=True)
    auto_pay = models.BooleanField(default=False)

    class Meta:
        db_table = '"cashflow"."transactions"'


class NotificationModel(BaseModel):
    planning = models.ForeignKey(PlanningModel, related_name='notifications', on_delete=models.CASCADE)
    trigger_date = models.DateField()
    message = models.TextField()
    related_transaction = models.ForeignKey(TransactionModel, null=True, blank=True, on_delete=models.SET_NULL)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = '"cashflow"."notifications"'
