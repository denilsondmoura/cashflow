from django.urls import path
from .views import PlanningView, BudgetView, TransactionView, PlanningUpdateView, PlanningDeleteView

urlpatterns = [
    path('planning/', PlanningView.as_view(), name='planning-list-create'),
    path('planning/<int:id>/update/', PlanningUpdateView.as_view(), name='planning-update'),
    path('planning/<int:id>/delete/', PlanningDeleteView.as_view(), name='planning-delete'),
    path('budget/', BudgetView.as_view(), name='budget-list'),
    path('transaction/', TransactionView.as_view(), name='transaction-list'),
]