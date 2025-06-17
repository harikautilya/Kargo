from django.test import TestCase
from unittest.mock import MagicMock
from ddt import ddt, data, unpack
from user.service import UserService
from user.dao import UserDao, OrganizationDao

@ddt
class TestUserService(TestCase):

    def setUp(self):
        self.mock_user_adapter = MagicMock()
        self.mock_org_adapter = MagicMock()

        self.service = UserService(
            user_adapter=self.mock_user_adapter, org_adapter=self.mock_org_adapter
        )

    @data(
        (
            UserDao(id=None, username="alice", password="pass123", display_name="test"),
            OrganizationDao(id=None, name="OrgX"),
            OrganizationDao(id=10, name="OrgX"),
            UserDao(
                id=1,
                username="alice",
                password="pass123",
                display_name="test",
            ),
        ),
    )
    @unpack
    def test_create_user(self, input_user, input_org, created_org, created_user):
        # Arrange
        self.mock_org_adapter.create_organization.return_value = created_org
        self.mock_user_adapter.create_user.return_value = created_user

        # Act
        result = self.service.create_user(user=input_user, org=input_org)

        # Assert
        self.assertEqual(result, created_user)
        self.mock_org_adapter.create_organization.assert_called_once_with(org=input_org)
        self.mock_user_adapter.create_user.assert_called_once_with(
            user=input_user, org=created_org
        )

        # Reset mocks for next run
        self.mock_org_adapter.reset_mock()
        self.mock_user_adapter.reset_mock()
