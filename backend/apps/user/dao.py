from dataclasses import dataclass

@dataclass(repr=True, eq=True, frozen=True)
class UserDao:
    """
    This is data class for service
    """

    username: str
    password: str | None
    display_name: str | None
    id: int | None

    @staticmethod
    def from_data(data: dict) -> "UserDao":
        username = data["username"]
        password = data["password"]
        display_name = data.get("display_name", None)
        id = data.get("id", None)

        return UserDao(
            username=username,
            password=password,
            display_name=display_name,
            id=id,
        )


@dataclass(repr=True, eq=True, frozen=True)
class OrganizationDao:
    """
    This is the data class for service
    """

    id: int | None
    name: str

    @staticmethod
    def from_data(data: dict):
        name = data["name"]
        id = data.get("id", None)
        return OrganizationDao(name=name, id=id)
