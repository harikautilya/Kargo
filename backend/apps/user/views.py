from rest_framework.views import APIView
from core.views import BaseJsonView
from dataclasses import dataclass
from .dao import *
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class CreateUserView(APIView):
    def put(self, request, pk):
        pass


class AuthView(APIView, BaseJsonView):

    @dataclass(repr=True, frozen=True, eq=True)
    class LoginUserView(User):
        pass

    def post(self, request):
        login_request = AuthView.LoginUserView.from_data(request.data)
        return self.ok_response({"hello": "there"})


class CreateOrganizationView(APIView, BaseJsonView):

    @dataclass(repr=True, frozen=True, eq=True)
    class CreateOrganizationRequest:
        user: User
        organization: Organization

        @staticmethod
        def from_data(data: dict):
            user = User.from_data(data["user"])
            organization = Organization.from_data(data["organization"])
            return CreateOrganizationView.CreateOrganizationRequest(
                user=user, organization=organization
            )

    def put(self, request):
        create_request = CreateOrganizationView.CreateOrganizationRequest.from_data(
            request.data
        )
        return self.ok_response({"hello": "there"})


class InviteCodeView(APIView, BaseJsonView):

    @dataclass(repr=True, frozen=True, eq=True)
    class UserInviteCode(User):
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
        
    def post(self, request):
        create_user = InviteCodeView.UserInviteCode.from_data(request.data)
        return self.ok_response({})
