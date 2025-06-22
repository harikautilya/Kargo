from rest_framework.views import APIView
from core.views import BaseJsonView
from dataclasses import dataclass

from .service import UserServiceFactory, AuthServiceFactory, InviteCodeFactory
from .requests import UserR, OrganizationR, UserRes, InviteCodeR, InviteCodeRes

import logging

logger = logging.getLogger(__name__)


# Create your views here.
class UserView(APIView, BaseJsonView):
    """
    View class for user details.
    This is auth protected.
    """

    def __init__(self, **kwargs) -> None:
        self.user_service = UserServiceFactory.create_user_service()

    def get(self, request):
        """
        Get user details.
        This returns the user details based on the token in header.
        """
        user = self.user_service.get_user(id=request.user_id)
        return self.ok_response({"user": UserRes.from_dao(user).to_json()})


class AuthView(APIView, BaseJsonView):
    """
    View class for user authentication.
    This is not auth protected at this instant.
    """

    @dataclass(repr=True, frozen=True, eq=True)
    class LoginUserView(UserR):
        pass

    def __init__(self, **kwargs) -> None:
        self.auth_service = AuthServiceFactory.create_auth_service()

    def post(self, request):
        """
        Generate auth token based on username and password provided
        """
        login_request = AuthView.LoginUserView.from_data(request.data)

        auth_token = self.auth_service.validate_user(user=login_request.to_dao())
        return self.ok_response({"token": auth_token})


class CreateOrganizationView(APIView, BaseJsonView):
    """
    View class for creating new organization.
    This not auth protected at this instant.
    Once roles are set out we would protect it behind an admin/owner role
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.user_service = UserServiceFactory.create_user_service()

    @dataclass(repr=True, frozen=True, eq=True)
    class CreateOrganizationRequest:
        """
        Request class for put request
        """

        user: UserR
        organization: OrganizationR

        @staticmethod
        def from_data(data: dict):
            user = UserR.from_data(data["user"])
            organization = OrganizationR.from_data(data["organization"])
            return CreateOrganizationView.CreateOrganizationRequest(
                user=user, organization=organization
            )

    def put(self, request):
        """
        Create organization and user.
        """
        create_request = CreateOrganizationView.CreateOrganizationRequest.from_data(
            request.data
        )
        user = self.user_service.create_user(
            user=create_request.user.to_dao(), org=create_request.organization.to_dao()
        )
        return self.ok_response({"user_id": user.id})


class InviteCodeView(APIView, BaseJsonView):
    """
    View class for invite code.
    This is partially auth protected.
    """

    @dataclass(repr=True, eq=True, frozen=True)
    class UserInviteCodeR:

        user: UserR
        code: InviteCodeR

        @staticmethod
        def from_data(data: dict) -> "InviteCodeView.UserInviteCodeR":
            user = UserR.from_data(data["user"])
            code = InviteCodeR.from_data(data["code"])
            return InviteCodeView.UserInviteCodeR(
                code=code,
                user=user,
            )

    def __init__(self, **kwargs) -> None:
        self.service = InviteCodeFactory.create_invite_code_service()

    def get(self, request):
        """
        Check if invite code is valid
        """
        invite_code = InviteCodeR.from_data(data=request.query_params)
        is_expired = self.service.is_code_valid(code=invite_code.code)
        if is_expired:
            return self.empty_ok()
        else:
            return self.bad_request()

    def patch(self, request):
        """
        Generate invite code based on user.
        User details are retervied via token
        """

        code = self.service.create_user_code(id=request.user_id)
        return self.ok_response(InviteCodeRes.from_dao(code).to_json())

    def post(self, request):
        """
        Check the invite code is validate.
        If yes, create user and respond ok
        If no, return not allowed status
        """
        create_user = InviteCodeView.UserInviteCodeR.from_data(request.data)
        is_created = self.service.create_user_using_code(
            user=create_user.user.to_dao(), invite_code=create_user.code.to_dao()
        )
        if is_created:
            return self.empty_ok()
        else:
            return self.bad_request()
