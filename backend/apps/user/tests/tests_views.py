from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class TestAuthView(APITestCase):

    def setUp(self):
        pass

    def test_post_login_user_request(self):
        url = "/user/login/"
        payload = {
            "username": "Sample",
            "password": "Sample",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestCreateOrganizationView(APITestCase):

    def setUp(self):
        pass

    def test_put_create_org_request(self):
        url = "/organization/"
        payload = {
            "user": {
                "username": "Sample",
                "password": "Sample",
                "display_name": "Sample",
            },
            "organization": {"name": "Sample"},
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestInviteCodeView(APITestCase):

    def setUp(self):
        pass
    
    def test_post_invite_code_request(self):
        url = "/organization/invite/"
        payload = {
            "username": "Sample",
            "password": "Sample",
            "display_name": "Sample",
            "code": "Sample",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
