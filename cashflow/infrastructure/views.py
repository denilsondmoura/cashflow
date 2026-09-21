from sys import exception
from decimal import Decimal
from datetime import date, datetime
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from cashflow.application.ports.inbound.commands.transaction_commands import CreateRecurringTransactionPlanningCommand, UpdateTransactionPlanningCommand
from cashflow.application.ports.inbound.commands.planning_commands import CreatePlanningCommand, UpdatePlanningCommand
from cashflow.application.ports.inbound.commands.budget_commands import CreateBudgetPlanningCommand, UpdateBudgetPlanningCommand
from .repositories import DjangoPlanningRepository, DjangoBudgetRepository, DjangoTransactionRepository
from cashflow.application.services import PlanningService

def get_planning_service():
    return PlanningService(
        planning_repo=DjangoPlanningRepository(),
        budget_repo=DjangoBudgetRepository(),
        transaction_repo=DjangoTransactionRepository(),
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
        
        name = request.POST.get('name') or None
        start_billing_cycle = int(request.POST.get('start_billing_cycle', 1)) or None
        end_date_str = request.POST.get('end_date') or None

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

        try: 
            planning_forecast_screen_dto = service.visualize_forecast_transactions_in_planning(id)
        except Exception as e:
            messages.error(request, f"Erro ao consultar movimentações previstas: {str(e)}")
            return redirect('planning-details', id)

        context = {
            "planning": planning_forecast_screen_dto.planning,
            "inflows_grouped": planning_forecast_screen_dto.inflows,
            "outflows_grouped": planning_forecast_screen_dto.outflows,
            "budgets": planning_forecast_screen_dto.budgets,
            "total_budget_formatted": planning_forecast_screen_dto.total_budget_formatted
        }
        return render(request, 'planing_forecast.html', context)


class PlanningCashflowView(LoginRequiredMixin, View):
    def get(self, request, id):
        service = get_planning_service()

        try: 
            planning_cashflow_screen_dto = service.visualise_cashflow_in_planning(id)
        except Exception as e:
            messages.error(request, f"Erro ao consultar fluxo de caixa: {str(e)}")
            return redirect('planning-details', id)

        context = {
            "planning": planning_cashflow_screen_dto.planning,
            "months_data": planning_cashflow_screen_dto.months_data,
            "budgets": planning_cashflow_screen_dto.budgets,
            "total_balance_formatted": planning_cashflow_screen_dto.total_balance_formatted,
            "diario_val_formatted": planning_cashflow_screen_dto.diario_val_formatted
        }

        return render(request, 'planing_cashflow.html', context)


class TransactionCreateView(LoginRequiredMixin, View):
    def post(self, request, id):
        service = get_planning_service()

        due_date_str = request.POST.get('due_date') or None
        description = request.POST.get('description') or None
        amount_str = request.POST.get('amount') or None
        transaction_type = request.POST.get('type') or None  # 'inflow' or 'outflow'
        cleared = request.POST.get('cleared') == 'on' or request.POST.get('cleared') == 'true'
        auto_pay = request.POST.get('auto_pay') == 'on' or request.POST.get('auto_pay') == 'true'
        repeat = request.POST.get('repeat') == 'on' or request.POST.get('repeat') == 'true'
        repeat_until_str = request.POST.get('repeat_until') or None
        iterations_str = request.POST.get('iterations') or None
        
        try:
            clean_amount = amount_str.replace('.', '').replace(',', '.')
            command = CreateRecurringTransactionPlanningCommand(
                planning_id=id,
                due_date=due_date_str,
                description=description,
                amount=Decimal(clean_amount),
                type=transaction_type,
                cleared=cleared,
                auto_pay=auto_pay,
                repeat=repeat,
                repeat_until=repeat_until_str,
                iterations=iterations_str
            )

            service.add_recurring_transaction_to_planning(command)
            messages.success(request, "Transação cadastrada com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao cadastrada transação: {str(e)}")

        return redirect(request.META.get('HTTP_REFERER', '/'))


class TransactionEditView(View):
    def post(self, request, id):
        service = get_planning_service()

        due_date_str = request.POST.get('due_date') or None
        description = request.POST.get('description') or None
        amount_str = request.POST.get('amount') or None
        cleared = request.POST.get('cleared') == 'on' or request.POST.get('cleared') == 'true'

        amount_val = Decimal(amount_str.replace('.', '').replace(',', '.'))
        try:
            command = UpdateTransactionPlanningCommand(
                id=id,
                due_date=due_date_str,
                description=description,
                amount=amount_val,
                cleared=cleared
            )

            service.update_transaction_in_planning(command)
            messages.success(request, "Transação atualizada com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar transação: {str(e)}")

        return redirect(request.META.get('HTTP_REFERER', '/'))


class TransactionDeleteView(View):
    def post(self, request, id):
        service = get_planning_service()

        try:
            service.remove_transaction_from_planning(id)
            messages.success(request, "Transação excluída com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao excluir transação: {str(e)}")

        return redirect(request.META.get('HTTP_REFERER', '/'))


class BudgetCreateView(View):
    def post(self, request, id):
        service = get_planning_service()

        description = request.POST.get('description')
        limit_amount_str = request.POST.get('amount')

        try:
            limit_amount_val = Decimal(limit_amount_str.replace('.', '').replace(',', '.'))
            command = CreateBudgetPlanningCommand(
                planning_id=id,
                current_balance=limit_amount_val,
                limit_amount=limit_amount_val,
                description=description
            )

            service.add_budget_to_planning(command)
            messages.success(request, "Orçamento criado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao criar orçamento: {str(e)}")

        return redirect(request.META.get('HTTP_REFERER', '/'))


class BudgetEditView(View):
    def post(self, request, id):
        service = get_planning_service()
            
        description = request.POST.get('description')
        limit_amount_str = request.POST.get('amount')

        try:
            limit_amount_val = Decimal(limit_amount_str.replace('.', '').replace(',', '.'))
            command = UpdateBudgetPlanningCommand(
                id=id,
                current_balance=limit_amount_val,
                limit_amount=limit_amount_val,
                description=description
            )

            service.update_budget_in_planning(command)
            messages.success(request, "Orçamento atualizado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar orçamento: {str(e)}")

        return redirect(request.META.get('HTTP_REFERER', '/'))


class BudgetDeleteView(View):
    def post(self, request, id):
        service = get_planning_service()

        try:
            service.remove_budget_from_planning(id)
            messages.success(request, "Orçamento excluído com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao excluir orçamento: {str(e)}")

        return redirect(request.META.get('HTTP_REFERER', '/'))
