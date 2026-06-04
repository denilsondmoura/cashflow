import calendar
import math
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
            
        planning_forecast_screen_dto = service.visualize_forecast_transactions_in_planning(id)
        
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
        def to_date(dt):
            if isinstance(dt, datetime):
                return dt.date()
            return dt
        
        service = get_planning_service()
        planning = service.planning_repo.find_by_id(id)
        if not planning:
            return redirect('planning-list-create')
            
        transactions = planning.transactions if planning.transactions else []
        
        MONTH_NAMES = {
            1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO",
            7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
        }
        
        start_date = to_date(planning.created_at) if planning.created_at else date.today()
        end_date = to_date(planning.end_date) if planning.end_date else date.today()
        
        months_in_range = []
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            months_in_range.append((current_date.year, current_date.month))
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        for tx in transactions:
            tx_date = to_date(tx.due_date)
            ym = (tx_date.year, tx_date.month)
            if ym not in months_in_range:
                months_in_range.append(ym)
                
        months_in_range = sorted(list(set(months_in_range)))
        
        total_balance = sum(b.current_balance for b in planning.budgets) if planning.budgets else Decimal('0.00')
        
        current_baseline = total_balance
        current_saldo = total_balance
        
        diario_val = planning.average_daily_expenditure if planning.average_daily_expenditure else Decimal('0.00')
        
        def format_currency(val):
            prefix = "-" if val < 0 else ""
            abs_val = abs(val)
            return f"{prefix}R$ {abs_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
        months_data = []
        for year, month in months_in_range:
            month_name = MONTH_NAMES.get(month, "OUTRO")
            _, num_days = calendar.monthrange(year, month)
            
            days_data = []
            for d in range(1, num_days + 1):
                day_date = date(year, month, d)
                
                day_inflows_txs = [t for t in transactions if to_date(t.due_date) == day_date and (t.type == "inflow" or t.amount >= 0)]
                day_inflow_sum = sum(t.amount for t in day_inflows_txs)
                
                day_outflows_txs = [t for t in transactions if to_date(t.due_date) == day_date and not (t.type == "inflow" or t.amount >= 0)]
                day_outflow_sum = sum(abs(t.amount) for t in day_outflows_txs)
                
                day_outflow_realized_sum = sum(abs(t.amount) for t in day_outflows_txs if t.cleared or t.auto_pay)
                
                current_baseline = current_baseline + day_inflow_sum - day_outflow_sum - diario_val
                current_saldo = current_saldo + day_inflow_sum - day_outflow_realized_sum - diario_val
                
                days_data.append({
                    "date_str": f"{d:02d}/{month:02d}",
                    "inflow_formatted": format_currency(day_inflow_sum) if day_inflow_sum > 0 else "-",
                    "outflow_formatted": format_currency(day_outflow_sum) if day_outflow_sum > 0 else "-",
                    "diario_formatted": format_currency(diario_val),
                    "saldo_formatted": format_currency(current_saldo),
                    "baseline_formatted": format_currency(current_baseline),
                })
                
            alerts = []
            if current_saldo < 0:
                alerts.append({
                    "type": "danger",
                    "message": f"Parece que nesse mês você vai terminar {format_currency(current_saldo)} no negativo, não seria a hora ideal para revisar seus gastos ou quem sabe buscar uma venda extra?"
                })
            else:
                alerts.append({
                    "type": "success",
                    "message": f"Parece que nesse mês vai sobrar {format_currency(current_saldo)}, que tal colocar na sua reserva de emergencia ou em algum item da sua lista de desejos?"
                })
                
            if current_saldo < current_baseline:
                diff = current_baseline - current_saldo
                days_to_recover = math.ceil(diff / diario_val) if diario_val > 0 else 0
                alerts.append({
                    "type": "warning",
                    "message": f"Seu saldo esta {format_currency(diff)} abaixo do planejado, mas nada que maneirar nos gastos por {days_to_recover} dias não resolva ;)"
                })
                
            months_data.append({
                "month_name": f"{month_name}",
                "days": days_data,
                "alerts": alerts
            })
            
        budget_list = []
        if planning.budgets:
            for b in planning.budgets:
                budget_list.append({
                    "id": b.id,
                    "description": b.description,
                    "amount_formatted": format_currency(b.current_balance)
                })
                
        context = {
            "planning": planning,
            "months_data": months_data,
            "budgets": budget_list,
            "total_balance_formatted": format_currency(total_balance),
            "diario_val_formatted": format_currency(diario_val)
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


        return redirect('planning-forecast', id=id)


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
