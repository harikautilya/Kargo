from abc import ABC, abstractmethod
from .serializers import UserSerializer, OrganizationSerializer, InviteCodeSeriazlizer
from .dao import UserDao, OrganizationDao, InviteCodeDao
from .models import User, Invitecode, Organization
from django.contrib.auth.hashers import verify_password
from datetime import datetime, timedelta, timezone
import random
import string
from django.conf import settings


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

    def validate_password(self, password: str, username: str) -> tuple[bool, int]:
        user = User.objects.only("password", "id").filter(username=username).first()
        if user is None:
            raise Exception(f"User with id not found : {username}")
        is_correct, _ = verify_password(password=password, encoded=user.password)

        return is_correct, user.id

    def get_user(self, id: int) -> UserDao:
        user = User.objects.filter(id=id).first()
        if user is None:
            raise Exception("User not found")

        return UserDao(
            id=user.id,
            username=user.username,
            password=None,
            display_name=user.display_name,
            orgid=user.org.id,
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
            user_model: User = serializer.save()
            return UserDao(
                id=user_model.id,
                username=user_model.username,
                display_name=user_model.display_name,
                password=None,
                orgid=user_model.org.id,
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

    @abstractmethod
    def get_organization(self, id: int) -> OrganizationDao:
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

    def get_organization(self, id: int) -> OrganizationDao:
        org = Organization.objects.filter(id=id).first()
        if org is None:
            raise Exception("Organization not found")
        return OrganizationDao(
            id=id,
            name=org.organization_name,
        )


#### Invite code class
class InviteCodeAdapter(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def create_invite_code(self, user: UserDao) -> InviteCodeDao:
        pass

    @abstractmethod
    def get_invite_code(self, code: str) -> InviteCodeDao | None:
        pass

    @abstractmethod
    def mark_expired(self, code: str) -> bool:
        pass


class InviteCodeModelAdpater(InviteCodeAdapter):

    def __init__(self) -> None:
        super().__init__()

    def generate_invite_code(self):
        # we can seed for better randomization. or maybe pre-generate, this itself is an entire arch.
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def create_invite_code(self, user: UserDao) -> InviteCodeDao:
        now = datetime.now(timezone.utc)
        data_dict = {
            "expiry_at": now
            + timedelta(milliseconds=settings.INVITE_CODE_EXPIRY_MILLS),
            "created_by": user.id,
            "expired": False,
            "code": self.generate_invite_code(),
        }
        serializer = InviteCodeSeriazlizer(data=data_dict)

        if serializer.is_valid():
            invite_code = serializer.save()
            if invite_code:
                return InviteCodeDao(
                    code=invite_code.code,
                    expiry_at=invite_code.expiry_at,
                    expired=invite_code.expired,
                    created_by=invite_code.created_by.id,
                )

        raise Exception(
            f"Seomthing went wrong while creating invite code {serializer.errors}"
        )

    def get_invite_code(self, code: str) -> InviteCodeDao | None:
        invite_code = Invitecode.objects.filter(code=code).first()
        if invite_code is None:
            return None
        return InviteCodeDao(
            code=invite_code.code,
            expiry_at=invite_code.expiry_at,
            expired=invite_code.expired,
            created_by=invite_code.created_by.id
        )

    def mark_expired(self, code: str) -> bool:
        Invitecode.objects.filter(code=code).update(expired=True)
        return True
