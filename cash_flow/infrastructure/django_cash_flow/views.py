import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .repositories import DjangoPlanningRepository, DjangoBudgetRepository, DjangoTransactionRepository
from cash_flow.application.services import PlanningService
from cash_flow.application.ports.inbound.commands.planning_commands import CreatePlanningCommand
from datetime import datetime

def get_planning_service():
    return PlanningService(
        planning_repo=DjangoPlanningRepository(),
        budget_repo=DjangoBudgetRepository(),
        transaction_repo=DjangoTransactionRepository()
    )

@method_decorator(csrf_exempt, name='dispatch')
class PlanningView(View):
    def get(self, request):
        service = get_planning_service()
        plannings = service.list_plannings()
        data = []
        if plannings:
            for p in plannings:
                data.append({
                    "id": p.id,
                    "name": p.name,
                    "color": p.color,
                    "end_date": p.end_date.isoformat(),
                    "status": p.status
                })
        return JsonResponse(data, safe=False)

    def post(self, request):
        service = get_planning_service()
        body = json.loads(request.body)
        command = CreatePlanningCommand(
            name=body['name'],
            color=body['color'],
            end_date=datetime.strptime(body['end_date'], '%Y-%m-%d').date()
        )
        planning = service.create_planning(command)
        return JsonResponse({
            "id": planning.id,
            "name": planning.name
        }, status=201)

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
