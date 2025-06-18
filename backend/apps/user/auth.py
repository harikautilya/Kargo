from typing import Any
import jwt
from .dao import UserDao


class Coder:
    """
    Base coder class
    """

    def __init__(self) -> None:
        pass

    def encode(self, obj: dict) -> str:
        """
        Encode dict
        """
        return jwt.encode(obj, "secret", algorithm="HS256")

    def decode(self, hash: str) -> dict:
        """
        Decode str
        """
        return jwt.decode(hash, "secret", algorithms=["HS256"])


class UserCoder(Coder):
    """
    User coder
    """

    def __init__(self) -> None:
        super().__init__()

    def encode_user(self, user: UserDao) -> str:
        """
        Encode user, we could probably have expriy_after but will address if time premits
        """
        data = {"user_id": user.id, "display_name": user.display_name}
        token = self.encode(data)

        return token

    def decode_user(self, hash: str) -> UserDao:
        """
        Decode user
        """
        data = self.decode(hash=hash)
        return UserDao(
            id=data["user_id"],
            display_name=data["display_name"],
            password=None,
            username="",
        )


class AuthMiddlware:
    """
    Auth Middleware for testing
    """

    allow_list = ["/user/login/"]

    def __init__(self, get_response):
        self.get_response = get_response
        self.user_coder = UserCoder()

    def __call__(self, request) -> Any:
        path = request.path
        if path not in self.allow_list:
            token = self.check_and_get_token(request.headers)
            user = self.user_coder.decode_user(token)
            request.user_id = user.id
        response = self.get_response(request)
        return response

    def check_and_get_token(self, headers):
    
        if "Authorization" not in headers:
            raise Exception("Auth token missing")
        token_header = headers["Authorization"]
        token_value = token_header.split(" ")
        return token_value[1]
