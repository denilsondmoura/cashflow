from django.urls import path
from .views import (
    PlanningView, BudgetView, TransactionView, PlanningUpdateView, 
    PlanningDeleteView, PlanningDetailsView, PlanningForecastView,
    TransactionEditView, TransactionDeleteView
)

urlpatterns = [
    path('planning/', PlanningView.as_view(), name='planning-list-create'),
    path('planning/<int:id>/', PlanningDetailsView.as_view(), name='planning-details'),
    path('planning/<int:id>/forecast/', PlanningForecastView.as_view(), name='planning-forecast'),
    path('planning/<int:id>/update/', PlanningUpdateView.as_view(), name='planning-update'),
    path('planning/<int:id>/delete/', PlanningDeleteView.as_view(), name='planning-delete'),
    path('budget/', BudgetView.as_view(), name='budget-list'),
    path('transaction/', TransactionView.as_view(), name='transaction-list'),
    path('transaction/<int:id>/edit/', TransactionEditView.as_view(), name='transaction-edit'),
    path('transaction/<int:id>/delete/', TransactionDeleteView.as_view(), name='transaction-delete'),
]