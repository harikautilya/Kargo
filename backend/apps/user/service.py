from .dao import UserDao, OrganizationDao, InviteCodeDao
from django.db import transaction
from .auth import UserCoder
from django.conf import settings
from .adapters import (
    UserAdapter,
    InviteCodeAdapter,
    UserModelAdapter,
    InviteCodeModelAdpater,
    OrganizationAdapter,
    OrganizationModelAdapter,
)
from datetime import datetime, timezone
import logging


### Service class
class UserService:

    def __init__(
        self,
        user_adapter: UserAdapter,
        org_adapter: OrganizationAdapter,
    ) -> None:
        self.user_adapter = user_adapter
        self.org_adapter = org_adapter

    def get_user(self, id: int) -> UserDao:
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


class InviteCodeService:

    def __init__(
        self,
        user_adpater: UserAdapter,
        invite_code_adapter: InviteCodeAdapter,
        org_adapter: OrganizationAdapter,
    ) -> None:
        self.user_adapter = user_adpater
        self.invite_code_adpater = invite_code_adapter
        self.org_adapter = org_adapter

    def create_user_code(self, id: int):
        user = self.user_adapter.get_user(id=id)
        invite_code = self.invite_code_adpater.create_invite_code(user=user)

        return InviteCodeDao(code=invite_code.code)

    def is_code_valid(self, code: str):
        now = datetime.now(timezone.utc)
        invite_code_dao = self.invite_code_adpater.get_invite_code(code=code)
        if invite_code_dao is None:
            # Invalid code provided
            logging.debug(f"Invalid code provided {code}")
            return False
        if invite_code_dao.expiry_at is None:
            raise Exception("Something went wrong while verifing the invite code")
        is_expired = now > invite_code_dao.expiry_at and invite_code_dao.expired
        
        return not is_expired

    @transaction.atomic
    def create_user_using_code(self, user: UserDao, invite_code: InviteCodeDao):
        # Check code validaty 
        is_valid = self.is_code_valid(code=invite_code.code)
        if not is_valid:
            raise Exception("Expired code is being used")
        
        # Get full details about the invite code
        hydrated_invite_code =  self.invite_code_adpater.get_invite_code(code=invite_code.code)
        if hydrated_invite_code is None or hydrated_invite_code.created_by is None:
            raise Exception("Something went wrong while hydration")
        
        # Mark code as expired
        is_marked = self.invite_code_adpater.mark_expired(code=hydrated_invite_code.code)
        if not is_marked:
            raise Exception("Something went wrong with marking expiry")
        created_by_user = self.user_adapter.get_user(id=hydrated_invite_code.created_by)

        org = OrganizationDao(
            id=created_by_user.orgid
        )
        return self.user_adapter.create_user(user=user, org=org)


class InviteCodeFactory:

    @staticmethod
    def create_invite_code_service() -> InviteCodeService:
        user_adapter = UserModelAdapter()
        invite_code_adapter = InviteCodeModelAdpater()
        org_adapter = OrganizationModelAdapter()
        return InviteCodeService(
            user_adpater=user_adapter,
            invite_code_adapter=invite_code_adapter,
            org_adapter=org_adapter,
        )
