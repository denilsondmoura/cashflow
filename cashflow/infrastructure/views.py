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
    from cashflow.infrastructure.presenters import DjangoTransactionGroupPresenter
    return PlanningService(
        planning_repo=DjangoPlanningRepository(),
        budget_repo=DjangoBudgetRepository(),
        transaction_repo=DjangoTransactionRepository(),
        presenter=DjangoTransactionGroupPresenter()
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
            
        grouped_data = service.list_grouped_transactions(id)
        inflows_grouped = grouped_data["inflows_grouped"]
        outflows_grouped = grouped_data["outflows_grouped"]
                
        budget_list = []
        total_budget = 0
        if planning.budgets:
            for b in planning.budgets:
                total_budget += b.limit_amount.value
                budget_list.append({
                    "id": b.id,
                    "description": b.description,
                    "amount_formatted": f"R$ {b.limit_amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "amount_raw": f"{b.limit_amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                })
        total_budget_formatted = f"R$ {total_budget:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
        context = {
            "planning": planning,
            "inflows_grouped": inflows_grouped,
            "outflows_grouped": outflows_grouped,
            "budgets": budget_list,
            "total_budget_formatted": total_budget_formatted
        }
        return render(request, 'planing_forecast.html', context)

class TransactionCreateView(LoginRequiredMixin, View):
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
        repeat_until_str = request.POST.get('repeat_until')
        iterations_str = request.POST.get('iterations')
        

        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            clean_amount = amount_str.replace('.', '').replace(',', '.')
            amount_val = Decimal(clean_amount)
            repeat_until = datetime.strptime(repeat_until_str, '%Y-%m-%d').date() if repeat_until_str else None
            iterations = int(iterations_str) if iterations_str else None
            
            if transaction_type == 'outflow' and amount_val > 0:
                amount_val = -amount_val
            elif transaction_type == 'inflow' and amount_val < 0:
                amount_val = abs(amount_val)

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


class BudgetCreateView(View):
    def post(self, request, id):
        from decimal import Decimal
        from django.contrib import messages
        from cashflow.application.ports.inbound.commands.budget_commands import CreateBudgetPlanningCommand
        from cashflow.domain.objects_values import Currency

        service = get_planning_service()
        description = request.POST.get('description')
        limit_amount_str = request.POST.get('amount')

        try:
            if not description or not description.strip():
                raise ValueError("Descrição do orçamento não informada!")
            if not limit_amount_str:
                raise ValueError("Valor limite do orçamento não informado!")

            limit_amount_val = Decimal(limit_amount_str.replace('.', '').replace(',', '.'))
            limit_amount = Currency(limit_amount_val)

            command = CreateBudgetPlanningCommand(
                planning_id=id,
                current_balance=limit_amount,
                limit_amount=limit_amount,
                description=description
            )

            service.add_budget_to_planning(command)
            messages.success(request, "Orçamento criado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao criar orçamento: {str(e)}")

        return redirect('planning-forecast', id=id)


class BudgetEditView(View):
    def post(self, request, id):
        from decimal import Decimal
        from django.contrib import messages
        from cashflow.application.ports.inbound.commands.budget_commands import UpdateBudgetPlanningCommand
        from cashflow.domain.objects_values import Currency

        service = get_planning_service()
        budget = service.budget_repo.find_by_id(id)
        if not budget:
            messages.error(request, "Orçamento não encontrado!")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        description = request.POST.get('description')
        limit_amount_str = request.POST.get('amount')

        try:
            if not description or not description.strip():
                raise ValueError("Descrição do orçamento não informada!")
            if not limit_amount_str:
                raise ValueError("Valor limite do orçamento não informado!")

            limit_amount_val = Decimal(limit_amount_str.replace('.', '').replace(',', '.'))
            limit_amount = Currency(limit_amount_val)

            command = UpdateBudgetPlanningCommand(
                id=id,
                current_balance=limit_amount,
                limit_amount=limit_amount,
                description=description
            )

            service.update_budget_in_planning(command)
            messages.success(request, "Orçamento atualizado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar orçamento: {str(e)}")

        return redirect('planning-forecast', id=budget.planning_id)


class BudgetDeleteView(View):
    def post(self, request, id):
        from django.contrib import messages
        service = get_planning_service()
        budget = service.budget_repo.find_by_id(id)
        if not budget:
            messages.error(request, "Orçamento não encontrado!")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        planning_id = budget.planning_id
        try:
            service.remove_budget_from_planning(id)
            messages.success(request, "Orçamento excluído com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao excluir orçamento: {str(e)}")

        return redirect('planning-forecast', id=planning_id)
