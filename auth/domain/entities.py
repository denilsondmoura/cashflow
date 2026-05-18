from dataclasses import dataclass
from datetime import date


@dataclass
class User:
    id: int
    password: str
    date_joined: date
    last_login: date
    is_superuser: bool
    username: str
    first_name: str
    last_name: str
    email: str
    is_staff: bool
    is_active: bool