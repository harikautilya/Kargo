from dataclasses import dataclass
from .dao import UserDao, OrganizationDao


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

    def toDao(self) -> UserDao:
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

    def toDao(self) -> OrganizationDao:
        return OrganizationDao(
            id=None,
            name=self.name,
        )
