from typing import Optional, List
from datetime import date
from django.shortcuts import get_object_or_404
from cashflow.domain.entities import Planning, Budget, Transaction, Notification
from cashflow.domain.objects_values import Currency
from .models import PlanningModel, BudgetModel, TransactionModel, NotificationModel
from cashflow.application.ports.outbound.repositories.planning_repository import PlanningRepository
from cashflow.application.ports.outbound.repositories.budget_repository import BudgetRepository
from cashflow.application.ports.outbound.repositories.transaction_repository import TransactionRepository
from cashflow.application.ports.outbound.repositories.notification_repository import NotificationRepository


class DjangoPlanningRepository(PlanningRepository):
    def _to_entity(self, model: PlanningModel) -> Planning:
        return Planning(
            id=model.id,
            name=model.name,
            color=model.color,
            end_date=model.end_date,
            average_daily_expenditure=Currency(model.average_daily_expenditure),
            total_budgeted_amount=Currency(model.total_budgeted_amount),
            total_balance_amount=Currency(model.total_balance_amount),
            budgets=[DjangoBudgetRepository._to_entity(b) for b in model.budgets.all()],
            transactions=[DjangoTransactionRepository._to_entity(t) for t in model.transactions.all()],
            notifications=[DjangoNotificationRepository._to_entity(n) for n in model.notifications.all()],
            updated_at=model.updated_at,
            status=model.status
        )

    def save(self, planning: Planning) -> Planning:
        data = {
            "name": planning.name,
            "color": planning.color,
            "end_date": planning.end_date,
            "average_daily_expenditure": planning.average_daily_expenditure.value,
            "total_budgeted_amount": planning.total_budgeted_amount.value,
            "total_balance_amount": planning.total_balance_amount.value,
            "status": planning.status
        }
        
        if planning.id == 0:
            model = PlanningModel.objects.create(**data)
        else:
            model = PlanningModel.objects.get(id=planning.id)
            for key, value in data.items():
                setattr(model, key, value)
            model.save()
            
        return self._to_entity(model)

    def find_by_id(self, id: int) -> Optional[Planning]:
        try:
            model = PlanningModel.objects.get(id=id)
            return self._to_entity(model)
        except PlanningModel.DoesNotExist:
            return None

    def list_all(self, page: int, page_size: int) -> Optional[List[Planning]]:
        start = (page - 1) * page_size
        end = start + page_size
        models = PlanningModel.objects.all()[start:end]
        return [self._to_entity(m) for m in models]

    def delete(self, id: int) -> bool:
        PlanningModel.objects.filter(id=id).delete()
        return True


class DjangoBudgetRepository(BudgetRepository):
    @staticmethod
    def _to_entity(model: BudgetModel) -> Budget:
        return Budget(
            id=model.id,
            current_balance=Currency(model.current_balance),
            limit_amount=Currency(model.limit_amount),
            description=model.description,
            planning_id=model.planning_id
        )

    def save(self, budget: Budget) -> Budget:
        data = {
            "current_balance": budget.current_balance.value,
            "limit_amount": budget.limit_amount.value,
            "description": budget.description,
            "planning_id": budget.planning_id
        }
        
        if budget.id == 0:
            model = BudgetModel.objects.create(**data)
        else:
            model = BudgetModel.objects.get(id=budget.id)
            for key, value in data.items():
                setattr(model, key, value)
            model.save()
            
        return self._to_entity(model)

    def find_by_id(self, id: int) -> Optional[Budget]:
        try:
            model = BudgetModel.objects.get(id=id)
            return self._to_entity(model)
        except BudgetModel.DoesNotExist:
            return None

    def list_all(self, page: int, page_size: int) -> Optional[List[Budget]]:
        start = (page - 1) * page_size
        end = start + page_size
        models = BudgetModel.objects.all()[start:end]
        return [self._to_entity(m) for m in models]

    def delete(self, id: int) -> bool:
        BudgetModel.objects.filter(id=id).delete()
        return True


class DjangoTransactionRepository(TransactionRepository):
    @staticmethod
    def _to_entity(model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            due_date=model.due_date,
            description=model.description,
            amount=Currency(model.amount),
            type=model.type,
            cleared=model.cleared,
            cleared_at=model.cleared_at,
            auto_pay=model.auto_pay,
            planning_id=model.planning_id
        )

    def save(self, transaction: Transaction) -> Transaction:
        data = {
            "due_date": transaction.due_date,
            "description": transaction.description,
            "amount": transaction.amount.value,
            "type": transaction.type,
            "cleared": transaction.cleared,
            "cleared_at": transaction.cleared_at,
            "auto_pay": transaction.auto_pay,
            "planning_id": transaction.planning_id
        }
        
        if transaction.id == 0:
            model = TransactionModel.objects.create(**data)
        else:
            model = TransactionModel.objects.get(id=transaction.id)
            for key, value in data.items():
                setattr(model, key, value)
            model.save()
            
        return self._to_entity(model)

    def find_by_id(self, id: int) -> Optional[Transaction]:
        try:
            model = TransactionModel.objects.get(id=id)
            return self._to_entity(model)
        except TransactionModel.DoesNotExist:
            return None

    def list_all(self, page: int, page_size: int) -> Optional[List[Transaction]]:
        start = (page - 1) * page_size
        end = start + page_size
        models = TransactionModel.objects.all()[start:end]
        return [self._to_entity(m) for m in models]

    def filter(
        self,
        data_from: Optional[date] = None,
        data_to: Optional[date] = None,
        description: Optional[str] = None,
        type: Optional[str] = None,
        cleared: Optional[bool] = None,
        auto_pay: Optional[bool] = None
    ) -> Optional[List[Transaction]]:
        filters = {}
        if data_from: filters["due_date__gte"] = data_from
        if data_to: filters["due_date__lte"] = data_to
        if description: filters["description__icontains"] = description
        if type: filters["type"] = type
        if cleared is not None: filters["cleared"] = cleared
        if auto_pay is not None: filters["auto_pay"] = auto_pay
        
        models = TransactionModel.objects.filter(**filters)
        return [self._to_entity(m) for m in models]

    def delete(self, id: int) -> bool:
        TransactionModel.objects.filter(id=id).delete()
        return True


class DjangoNotificationRepository(NotificationRepository):
    @staticmethod
    def _to_entity(model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            trigger_date=model.trigger_date,
            message=model.message,
            related_transaction_id=model.related_transaction_id,
            is_read=model.is_read,
            planning_id=model.planning_id
        )

    def save(self, notification: Notification) -> Notification:
        data = {
            "trigger_date": notification.trigger_date,
            "message": notification.message,
            "related_transaction_id": notification.related_transaction_id,
            "is_read": notification.is_read,
            "planning_id": notification.planning_id
        }
        
        if notification.id == 0:
            model = NotificationModel.objects.create(**data)
        else:
            model = NotificationModel.objects.get(id=notification.id)
            for key, value in data.items():
                setattr(model, key, value)
            model.save()
            
        return self._to_entity(model)

    def find_by_id(self, id: int) -> Optional[Notification]:
        try:
            model = NotificationModel.objects.get(id=id)
            return self._to_entity(model)
        except NotificationModel.DoesNotExist:
            return None

    def list_all(self, page: int, page_size: int) -> Optional[list[Notification]]:
        start = (page - 1) * page_size
        end = start + page_size
        models = NotificationModel.objects.all()[start:end]
        return [self._to_entity(m) for m in models]

    def delete(self, id: int) -> bool:
        NotificationModel.objects.filter(id=id).delete()
        return True
