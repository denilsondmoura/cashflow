import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from .repositories import DjangoPlanningRepository, DjangoBudgetRepository, DjangoTransactionRepository
from cashflow.application.services import PlanningService
from cashflow.application.ports.inbound.commands.planning_commands import CreatePlanningCommand
from datetime import datetime

def get_planning_service():
    return PlanningService(
        planning_repo=DjangoPlanningRepository(),
        budget_repo=DjangoBudgetRepository(),
        transaction_repo=DjangoTransactionRepository()
    )

class PlanningView(LoginRequiredMixin, View):
    def get(self, request):
        service = get_planning_service()
        plannings = service.list_plannings()
        return render(request, 'planning_list.html', {'plannings': plannings})

    def post(self, request):
        service = get_planning_service()
        
        name = request.POST.get('name')
        color = request.POST.get('color')
        end_date_str = request.POST.get('end_date')

        command = CreatePlanningCommand(
            name=name,
            color=color,
            end_date=datetime.strptime(end_date_str, '%Y-%m-%d').date()
        )
        service.create_planning(command)
        
        return redirect('planning-list-create')

@method_decorator(csrf_exempt, name='dispatch')
class BudgetView(View):
    def get(self, request):
        service = get_planning_service()
        budgets = service.list_budgets()
        data = []
        if budgets:
            for b in budgets:
                data.append({
                    "id": b.id,
                    "description": b.description,
                    "limit_amount": float(b.limit_amount.value),
                    "current_balance": float(b.current_balance.value),
                    "planning_id": b.planning_id
                })
        return JsonResponse(data, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class TransactionView(View):
    def get(self, request):
        service = get_planning_service()
        # For simplicity, listing all. Filtering can be added later.
        transactions = service.transaction_repo.list_all(page=1, page_size=100)
        data = []
        if transactions:
            for t in transactions:
                data.append({
                    "id": t.id,
                    "description": t.description,
                    "amount": float(t.amount.value),
                    "due_date": t.due_date.isoformat(),
                    "type": t.type,
                    "cleared": t.cleared
                })
        return JsonResponse(data, safe=False)
