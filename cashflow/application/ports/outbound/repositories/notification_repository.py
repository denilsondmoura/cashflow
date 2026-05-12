from abc import ABC, abstractmethod
from cashflow.domain.entities import Notification
from typing import Optional

class NotificationRepository(ABC):
    @abstractmethod
    def save(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Notification]:
        pass

    @abstractmethod
    def list_all(self, page: int, page_size: int) -> Optional[list[Notification]]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
