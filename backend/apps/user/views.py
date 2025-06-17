from rest_framework.views import APIView
from core.views import BaseJsonView
from dataclasses import dataclass
from .service import UserServiceFactory
from .requests import UserR, OrganizationR
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class UserView(APIView, BaseJsonView):
    """
    View class for user details.
    This is auth protected.
    """

    def get(self, request):
        """
        Get user details.
        This returns the user details based on the token in header.
        """
        pass


class AuthView(APIView, BaseJsonView):
    """
    View class for user authentication.
    This is not auth protected at this instant.
    """

    @dataclass(repr=True, frozen=True, eq=True)
    class LoginUserView(UserR):
        pass

    def post(self, request):
        """
        Generate auth token based on username and password provided
        """
        login_request = AuthView.LoginUserView.from_data(request.data)
        return self.ok_response({"hello": "there"})


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
            user=create_request.user.toDao(), org=create_request.organization.toDao()
        )
        return self.ok_response({"user_id": user.id})


class InviteCodeView(APIView, BaseJsonView):
    """
    View class for invite code.
    This is auth protected.
    """

    @dataclass(repr=True, frozen=True, eq=True)
    class UserInviteCode(UserR):
        """
        Request class for post request
        """

        code: str

        @staticmethod
        def from_data(data: dict) -> "InviteCodeView.UserInviteCode":
            username = data["username"]
            password = data["password"]
            display_name = data.get("display_name", None)
            code = data["code"]
            return InviteCodeView.UserInviteCode(
                username=username,
                password=password,
                display_name=display_name,
                id=None,
                code=code,
            )

    def get(self, request):
        """
        Check if invite code is valid
        """
        pass

    def patch(self, request):
        """
        Generate invite code based on user.
        User details are retervied via token
        """
        pass

    def post(self, request):
        """
        Check the invite code is validate.
        If yes, create user and respond ok
        If no, return not allowed status
        """
        create_user = InviteCodeView.UserInviteCode.from_data(request.data)
        return self.ok_response({})
