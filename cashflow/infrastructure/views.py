import json
from collections import defaultdict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from .repositories import DjangoPlanningRepository, DjangoBudgetRepository, DjangoTransactionRepository
from cashflow.application.services import PlanningService
from cashflow.application.ports.inbound.commands.planning_commands import CreatePlanningCommand, UpdatePlanningCommand
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
        plannings = service.list_plannings(username=request.user.username)
        return render(request, 'planning_list.html', {'plannings': plannings})

    def post(self, request):
        service = get_planning_service()
        
        name = request.POST.get('name')
        start_billing_cycle = int(request.POST.get('start_billing_cycle', 1))
        end_date_str = request.POST.get('end_date')

        command = CreatePlanningCommand(
            name=name,
            end_date=datetime.strptime(end_date_str, '%Y-%m-%d').date(),
            start_billing_cycle=start_billing_cycle,
            created_by=request.user.username
        )
        service.create_planning(command)
        
        return redirect('planning-list-create')


class PlanningUpdateView(LoginRequiredMixin, View):
    def post(self, request, id):
        service = get_planning_service()
        
        name = request.POST.get('name')
        start_billing_cycle = int(request.POST.get('start_billing_cycle', 1))
        end_date_str = request.POST.get('end_date')

        command = UpdatePlanningCommand(
            id=id,
            name=name,
            end_date=datetime.strptime(end_date_str, '%Y-%m-%d').date(),
            start_billing_cycle=start_billing_cycle,
            updated_by=request.user.username
        )
        service.update_planning(command)
        
        return redirect('planning-list-create')


class PlanningDeleteView(LoginRequiredMixin, View):
    def post(self, request, id):
        service = get_planning_service()
        service.delete_planning(id)
        return redirect('planning-list-create')


class PlanningDetailsView(LoginRequiredMixin, View):
    def get(self, request, id):
        service = get_planning_service()
        planning = service.planning_repo.find_by_id(id)
        if not planning:
            return redirect('planning-list-create')
        return render(request, 'planning_details.html', {'planning': planning})


class PlanningForecastView(LoginRequiredMixin, View):
    def get(self, request, id):
        service = get_planning_service()
        planning = service.planning_repo.find_by_id(id)
        if not planning:
            return redirect('planning-list-create')
            
        MONTH_NAMES = {
            1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO",
            7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
        }
        
        inflows_by_month = defaultdict(list)
        outflows_by_month = defaultdict(list)
        
        if planning.transactions:
            for t in planning.transactions:
                month_name = MONTH_NAMES.get(t.due_date.month, "OUTRO")
                if t.type == "inflow" or t.amount.value >= 0:
                    inflows_by_month[month_name].append(t)
                else:
                    outflows_by_month[month_name].append(t)
                    
        if not inflows_by_month and not outflows_by_month:
            mock_inflows_junho = [
                {"due_date_str": "01/06", "description": "salário empresa A", "amount_formatted": "R$ 5.300,00"},
                {"due_date_str": "02/06", "description": "salário empresa B", "amount_formatted": "R$ 1.800,00"},
                {"due_date_str": "03/06", "description": "Restituição IR", "amount_formatted": "R$ 1.800,00"},
                {"due_date_str": "04/06", "description": "ticket", "amount_formatted": "R$ 600,00"},
            ]
            inflows_grouped = [
                {"month": "JUNHO", "transactions": mock_inflows_junho, "total_formatted": "R$ 9.500,00"},
                {"month": "JULHO", "transactions": [], "total_formatted": "R$ 9.100,00"},
                {"month": "AGOSTO", "transactions": [], "total_formatted": "R$ 9.100,00"},
            ]
            
            mock_outflows_junho = [
                {"due_date_str": "01/06", "description": "fatura do cartão", "amount_formatted": "R$ 1.300,00"},
                {"due_date_str": "02/06", "description": "conta de energia", "amount_formatted": "R$ 200,00"},
                {"due_date_str": "03/06", "description": "Seguro da moto", "amount_formatted": "R$ 116,00"},
                {"due_date_str": "04/06", "description": "Monitor philips evnia", "amount_formatted": "R$ 800,00"},
            ]
            outflows_grouped = [
                {"month": "JUNHO", "transactions": mock_outflows_junho, "total_formatted": "R$ 2.416,00"},
                {"month": "JULHO", "transactions": [], "total_formatted": "R$ 9.100,00"},
                {"month": "AGOSTO", "transactions": [], "total_formatted": "R$ 9.100,00"},
            ]
        else:
            inflows_grouped = []
            for month_name, txs in inflows_by_month.items():
                total = sum(tx.amount.value for tx in txs)
                tx_list = []
                for tx in txs:
                    tx_list.append({
                        "id": tx.id,
                        "due_date_str": tx.due_date.strftime("%d/%m"),
                        "due_date_iso": tx.due_date.strftime("%Y-%m-%d"),
                        "description": tx.description,
                        "amount_formatted": f"R$ {tx.amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "amount_raw": f"{tx.amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "cleared": tx.cleared,
                        "type": tx.type
                    })
                inflows_grouped.append({
                    "month": month_name,
                    "transactions": tx_list,
                    "total_formatted": f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                })
                
            outflows_grouped = []
            for month_name, txs in outflows_by_month.items():
                total = sum(abs(tx.amount.value) for tx in txs)
                tx_list = []
                for tx in txs:
                    tx_list.append({
                        "id": tx.id,
                        "due_date_str": tx.due_date.strftime("%d/%m"),
                        "due_date_iso": tx.due_date.strftime("%Y-%m-%d"),
                        "description": tx.description,
                        "amount_formatted": f"R$ {abs(tx.amount.value):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "amount_raw": f"{abs(tx.amount.value):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        "cleared": tx.cleared,
                        "type": tx.type
                    })
                outflows_grouped.append({
                    "month": month_name,
                    "transactions": tx_list,
                    "total_formatted": f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                })
                
        if planning.budgets:
            budget_list = []
            total_budget = 0
            for b in planning.budgets:
                total_budget += b.limit_amount.value
                budget_list.append({
                    "description": b.description,
                    "amount_formatted": f"R$ {b.limit_amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                })
            total_budget_formatted = f"R$ {total_budget:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            budget_list = [
                {"description": "supermercado", "amount_formatted": "R$ 1.100,00"},
                {"description": "lanches", "amount_formatted": "R$ 300,00"},
                {"description": "ração dos PETs", "amount_formatted": "R$ 300,00"},
                {"description": "combustível", "amount_formatted": "R$ 140,00"},
            ]
            total_budget_formatted = "R$ 2.416,00"
            
        context = {
            "planning": planning,
            "inflows_grouped": inflows_grouped,
            "outflows_grouped": outflows_grouped,
            "budgets": budget_list,
            "total_budget_formatted": total_budget_formatted
        }
        return render(request, 'forecast_transactions.html', context)

    def post(self, request, id):
        from decimal import Decimal
        from django.contrib import messages
        from cashflow.application.ports.inbound.commands.transaction_commands import CreateRecurringTransactionPlanningCommand
        from cashflow.domain.objects_values import Currency

        service = get_planning_service()
        planning = service.planning_repo.find_by_id(id)
        if not planning:
            return redirect('planning-list-create')

        due_date_str = request.POST.get('due_date')
        description = request.POST.get('description')
        amount_str = request.POST.get('amount')
        transaction_type = request.POST.get('type')  # 'inflow' or 'outflow'
        cleared = request.POST.get('cleared') == 'on' or request.POST.get('cleared') == 'true'
        auto_pay = request.POST.get('auto_pay') == 'on' or request.POST.get('auto_pay') == 'true'
        repeat = request.POST.get('repeat') == 'on' or request.POST.get('repeat') == 'true'

        try:
            if not due_date_str:
                raise ValueError("Data prevista da transação não informada")
            if not description or not description.strip():
                raise ValueError("Descrição da transação não informada")
            if not amount_str:
                raise ValueError("Valor da transação não informado")

            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            clean_amount = amount_str.replace('.', '').replace(',', '.')
            amount_val = Decimal(clean_amount)
            
            if transaction_type == 'outflow' and amount_val > 0:
                amount_val = -amount_val
            elif transaction_type == 'inflow' and amount_val < 0:
                amount_val = abs(amount_val)

            repeat_until = None
            iterations = None
            if repeat:
                repeat_until_str = request.POST.get('repeat_until')
                if repeat_until_str:
                    repeat_until = datetime.strptime(repeat_until_str, '%Y-%m-%d').date()
                
                iterations_str = request.POST.get('iterations')
                if iterations_str:
                    iterations = int(iterations_str)

            command = CreateRecurringTransactionPlanningCommand(
                planning_id=id,
                due_date=due_date,
                description=description,
                amount=Currency(amount_val),
                cleared=cleared,
                auto_pay=auto_pay,
                repeat=repeat,
                repeat_until=repeat_until,
                iterations=iterations
            )

            service.add_recurring_transaction_to_planning(command)
            messages.success(request, "Transação cadastrada com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao criar transação: {str(e)}")

        return redirect('planning-forecast', id=id)


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


class TransactionEditView(View):
    def post(self, request, id):
        from decimal import Decimal
        from django.contrib import messages
        from datetime import datetime
        from cashflow.application.ports.inbound.commands.transaction_commands import UpdateTransactionPlanningCommand
        from cashflow.domain.objects_values import Currency

        service = get_planning_service()
        transaction = service.transaction_repo.find_by_id(id)
        if not transaction:
            messages.error(request, "Transação não encontrada!")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        due_date_str = request.POST.get('due_date')
        description = request.POST.get('description')
        amount_str = request.POST.get('amount')
        cleared = request.POST.get('cleared') == 'on' or request.POST.get('cleared') == 'true'

        try:
            if not due_date_str:
                raise ValueError("Data prevista não informada")
            if not description or not description.strip():
                raise ValueError("Descrição não informada")
            if not amount_str:
                raise ValueError("Valor não informado")

            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            amount_val = Decimal(amount_str.replace('.', '').replace(',', '.'))
            
            if transaction.type == 'outflow' and amount_val > 0:
                amount_val = -amount_val
            elif transaction.type == 'inflow' and amount_val < 0:
                amount_val = abs(amount_val)

            cleared_at = datetime.now().date() if cleared else None

            command = UpdateTransactionPlanningCommand(
                id=id,
                due_date=due_date,
                description=description,
                amount=Currency(amount_val),
                cleared=cleared,
                cleared_at=cleared_at,
                auto_pay=transaction.auto_pay,
                repeat=False,
                iterations=0,
                repeat_until=None
            )

            service.update_transaction_in_planning(command)
            messages.success(request, "Transação atualizada com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar transação: {str(e)}")

        return redirect('planning-forecast', id=transaction.planning_id)


class TransactionDeleteView(View):
    def post(self, request, id):
        from django.contrib import messages
        service = get_planning_service()
        transaction = service.transaction_repo.find_by_id(id)
        if not transaction:
            messages.error(request, "Transação não encontrada!")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        planning_id = transaction.planning_id
        try:
            service.remove_transaction_from_planning(id)
            messages.success(request, "Transação excluída com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao excluir transação: {str(e)}")

        return redirect('planning-forecast', id=planning_id)
