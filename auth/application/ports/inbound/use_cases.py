from abc import ABC, abstractmethod
from auth.application.DTOs.commands import RegisterUserCommand

class UserUseCase(ABC):

    @abstractmethod
    def register(self, command: RegisterCommand) -> None:
        pass

    @abstractmethod
    def login(self, command: LoginCommand) -> None:
        pass
    
    @abstractmethod
    def logout(self) -> None:
        pass

    @abstractmethod
    def password_reset(self, command: PasswordResetCommand) -> None:
        pass
    
    @abstractmethod
    def password_reset_done(self, command: PasswordResetDoneCommand) -> None:
        pass
    
    @abstractmethod
    def password_reset_confirm(self, command: PasswordResetConfirmCommand) -> None:
        pass
    
    @abstractmethod
    def password_reset_complete(self, command: PasswordResetCompleteCommand) -> None:
        pass
    
    @abstractmethod
    def get_user(self, user: User) -> User:
        pass
    
    @abstractmethod
    def update_user(self, user: User) -> User:
        pass

    
