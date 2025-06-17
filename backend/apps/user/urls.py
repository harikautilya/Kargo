from django.urls import path
from .views import CreateUserView, InviteCodeView, CreateOrganizationView, AuthView

organization_url = [
    path("organization/", CreateOrganizationView.as_view(), name="organization"),
    path("organization/invite/", InviteCodeView.as_view(), name="invite-user"),
]

user_urls = [
    path("user/", CreateUserView.as_view(), name="user"),
    path("user/login/", AuthView.as_view(), name="user-login"),
]

urlpatterns = organization_url + user_urls
