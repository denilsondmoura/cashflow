from django.urls import path
from .views import (
    PlanningView, PlanningUpdateView, 
    PlanningDeleteView, PlanningDetailsView, PlanningForecastView,
    PlanningCashflowView,
    TransactionEditView, TransactionDeleteView, TransactionCreateView,
    BudgetCreateView, BudgetEditView, BudgetDeleteView
)

urlpatterns = [
    path('planning/', PlanningView.as_view(), name='planning-list-create'),
    path('planning/<int:id>/', PlanningDetailsView.as_view(), name='planning-details'),
    path('planning/<int:id>/update/', PlanningUpdateView.as_view(), name='planning-update'),
    path('planning/<int:id>/delete/', PlanningDeleteView.as_view(), name='planning-delete'),
    path('planning/<int:id>/forecast/', PlanningForecastView.as_view(), name='planning-forecast'),
    path('planning/<int:id>/forecast/transaction/add/', TransactionCreateView.as_view(), name='transaction-create'),
    path('planning/<int:id>/forecast/budget/add/', BudgetCreateView.as_view(), name='budget-create'),
    path('planning/<int:id>/cashflow/', PlanningCashflowView.as_view(), name='planning-cashflow'),
    path('transaction/<int:id>/edit/', TransactionEditView.as_view(), name='transaction-edit'),
    path('transaction/<int:id>/delete/', TransactionDeleteView.as_view(), name='transaction-delete'),
    path('budget/<int:id>/edit/', BudgetEditView.as_view(), name='budget-edit'),
    path('budget/<int:id>/delete/', BudgetDeleteView.as_view(), name='budget-delete'),
]