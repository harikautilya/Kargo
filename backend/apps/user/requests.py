from dataclasses import dataclass
from .dao import UserDao, OrganizationDao, InviteCodeDao


@dataclass(repr=True, eq=True, frozen=True)
class UserR:
    """
    This is data class for request object of user
    """

    username: str
    password: str
    display_name: str | None
    id: int | None

    @staticmethod
    def from_data(data: dict) -> "UserR":
        username = data["username"]
        password = data["password"]
        display_name = data.get("display_name", None)
        id = data.get("id", None)

        return UserR(
            username=username,
            password=password,
            display_name=display_name,
            id=id,
        )

    def to_dao(self) -> UserDao:
        return UserDao(
            id=None,
            username=self.username,
            password=self.password,
            display_name=self.display_name,
        )


@dataclass(repr=True, eq=True, frozen=True)
class OrganizationR:
    """
    This is the data class for request object of organization
    """

    name: str

    @staticmethod
    def from_data(data: dict) -> "OrganizationR":
        name = data["name"]
        return OrganizationR(name=name)

    def to_dao(self) -> OrganizationDao:
        return OrganizationDao(
            id=None,
            name=self.name,
        )


@dataclass(repr=True, eq=True, frozen=True)
class InviteCodeR:
    """
    This is the data class for service
    """

    code: str

    @staticmethod
    def from_data(data: dict) -> "InviteCodeR":
        invite_code = data["invite_code"]
        return InviteCodeR(code=invite_code)

    def to_dao(
        self,
    ) -> InviteCodeDao:
        return InviteCodeDao(code=self.code)


@dataclass(repr=True, eq=True, frozen=True)
class UserRes:
    """
    This is data class for request object of user
    """

    display_name: str
    id: int

    @staticmethod
    def from_dao(data: UserDao) -> "UserRes":
        return UserRes(
            display_name=data.display_name,  # type: ignore
            id=data.id,  # type: ignore
        )

    def to_json(self):
        return {
            "id": self.id,
            "display_name": self.display_name,
        }


@dataclass(repr=True, eq=True, frozen=True)
class InviteCodeRes:

    code: str

    @staticmethod
    def from_dao(data: InviteCodeDao) -> "InviteCodeRes":
        return InviteCodeRes(
            code=data.code,
        )

    def to_json(self):
        return {"code": self.code}
