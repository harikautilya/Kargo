from abc import ABC, abstractmethod
from .serializers import UserSerializer, OrganizationSerializer
from .dao import UserDao, OrganizationDao
from django.db import transaction


#### User classes
class UserAdapter(ABC):
    """
    User adapater
    """

    def __init__(self) -> None:
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
        self, user_adapter: UserAdapter, org_adapter: OrganizationAdapter
    ) -> None:
        self.user_adapter = user_adapter
        self.org_adapter = org_adapter

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
