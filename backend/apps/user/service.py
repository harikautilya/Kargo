from abc import ABC, abstractmethod
from .serializers import UserSerializer, OrganizationSerializer
from .dao import UserDao, OrganizationDao
from .models import User, Organization
from django.contrib.auth.hashers import verify_password
from django.db import transaction
from .auth import UserCoder


#### User classes
class UserAdapter(ABC):
    """
    User adapater
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def validate_password(self, password: str, username: str) -> tuple[bool, int]:
        pass

    @abstractmethod
    def get_user(self, id: int) -> UserDao:
        pass

    @abstractmethod
    def create_user(self, user: UserDao, org: OrganizationDao) -> UserDao:
        pass


class UserModelAdapter(UserAdapter):
    """
    Adapter using models
    """

    def __init__(self) -> None:
        super().__init__()

    def validate_password(self, password: str, username: str) ->  tuple[bool, int]:
        user = User.objects.only("password", "id").filter(username=username).first()
        if user is None:
            raise Exception(f"User with id not found : {username}")
        is_correct, _ = verify_password(password=password, encoded=user.password)

        return is_correct , user.id

    def get_user(self, id: int) -> UserDao:
        user = User.objects.filter(id=id).first()
        if user is None:
            raise Exception("User not found")

        return UserDao(
            id=user.id,
            username=user.username,
            password=None,
            display_name=user.display_name,
        )

    def create_user(self, user: UserDao, org: OrganizationDao) -> UserDao:
        user_dict = {
            "username": user.username,
            "password": user.password,
            "display_name": user.display_name,
            "org": org.id,
        }
        serializer = UserSerializer(data=user_dict)
        if serializer.is_valid():
            user = serializer.save()
            return UserDao(
                id=user.id,
                username=user.username,
                display_name=user.display_name,
                password=None,
            )
        raise Exception(f"Something went wrong creating user: {serializer.errors}")


#### Organization classes
class OrganizationAdapter(ABC):
    """
    Organization adapter
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def create_organization(self, org: OrganizationDao) -> OrganizationDao:
        pass


class OrganizationModelAdapter(OrganizationAdapter):
    """
    Adapter using models
    """

    def __init__(self) -> None:
        super().__init__()

    def create_organization(self, org: OrganizationDao) -> OrganizationDao:
        org_dict = {"organization_name": org.name}

        serializer = OrganizationSerializer(data=org_dict)
        if serializer.is_valid():
            org_model = serializer.save()
            return OrganizationDao(id=org_model.id, name=org_model.organization_name)
        raise Exception(
            f"Something went wrong creating organization:  {serializer.errors}"
        )


### Service class
class UserService:

    def __init__(
        self,
        user_adapter: UserAdapter,
        org_adapter: OrganizationAdapter,
    ) -> None:
        self.user_adapter = user_adapter
        self.org_adapter = org_adapter

    def get_user(self, id:int) -> UserDao:
        return self.user_adapter.get_user(id=id)


    @transaction.atomic
    def create_user(self, user: UserDao, org: OrganizationDao) -> UserDao:
        org = self.org_adapter.create_organization(org=org)
        return self.user_adapter.create_user(user=user, org=org)


class UserServiceFactory:
    """
    Factory for user service, This is not thread safe yet.
    """

    _instance = None

    @classmethod
    def create_user_service(cls):
        if cls._instance is None:
            user_adatper = UserModelAdapter()
            org_adapter = OrganizationModelAdapter()
            cls._instance = UserService(
                user_adapter=user_adatper, org_adapter=org_adapter
            )
        return cls._instance


class AuthService:
    """
    Service class for authentication purpose
    """

    def __init__(self, user_adapter: UserAdapter) -> None:
        self.user_adapter = user_adapter
        self.coder = UserCoder()

    def validate_user(self, user: UserDao) -> str:
        if user.password is None or user.username is None:
            raise Exception("Details missing")

        is_correct_password, user_id = self.user_adapter.validate_password(
            password=user.password,
            username=user.username,
        )
        if is_correct_password:
            user = self.user_adapter.get_user(id=user_id)
            return self.coder.encode_user(user=user)

        raise Exception("Invalid details provided")


class AuthServiceFactory:
    """
    Factory for auth service, This is not thread safe yet.
    """

    _instance = None

    @classmethod
    def create_auth_service(cls):
        if cls._instance is None:
            user_adatper = UserModelAdapter()
            cls._instance = AuthService(user_adapter=user_adatper)
        return cls._instance
