from dataclasses import dataclass


@dataclass(repr=True, eq=True, frozen=True)
class User:
    """
    This is data class for request object of user
    """

    username: str
    password: str
    display_name: str | None
    id: int | None

    @staticmethod
    def from_data(data: dict) -> 'User':
        username = data["username"]
        password = data["password"]
        display_name = data.get("display_name", None)
        id = data.get("id", None)

        return User(
            username=username,
            password=password,
            display_name=display_name,
            id=id,
        )


@dataclass(repr=True, eq=True, frozen=True)
class Organization:
    """
    This is the data class for request object of organization
    """

    name: str

    @staticmethod
    def from_data(data: dict):
        name = data["name"]
        return Organization(name=name)
