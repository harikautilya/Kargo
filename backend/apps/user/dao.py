from dataclasses import dataclass
from datetime import datetime


@dataclass(repr=True, eq=True, frozen=True)
class OrganizationDao:
    """
    This is the data class for service
    """

    id: int | None
    name: str  | None = None

    @staticmethod
    def from_data(data: dict):
        name = data["name"]
        id = data.get("id", None)
        return OrganizationDao(name=name, id=id)


@dataclass(repr=True, eq=True, frozen=True)
class UserDao:
    """
    This is data class for service
    """

    username: str
    password: str | None
    display_name: str | None
    id: int | None
    orgid: int | None = None

    @staticmethod
    def from_data(data: dict) -> "UserDao":
        username = data["username"]
        password = data["password"]
        display_name = data.get("display_name", None)
        id = data.get("id", None)

        return UserDao(
            username=username, password=password, display_name=display_name, id=id
        )


@dataclass(repr=True, eq=True, frozen=True)
class InviteCodeDao:
    """
    This is the data class for service
    """

    code: str
    expiry_at: datetime | None = None
    expired: bool | None = None
    created_by: int | None = None
    used_by: int | None = None
