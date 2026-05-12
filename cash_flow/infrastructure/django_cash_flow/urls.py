from django.urls import path
from .views import PlanningView, BudgetView, TransactionView

urlpatterns = [
    path('planning/', PlanningView.as_view(), name='planning-list-create'),
    path('budget/', BudgetView.as_view(), name='budget-list'),
    path('transaction/', TransactionView.as_view(), name='transaction-list'),
]