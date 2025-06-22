from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Organization, Invitecode


class UserSerializer(serializers.ModelSerializer):
    """
    User model serializer
    """

    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "display_name", "username", "password", "org"]

    def create(self, validated_data):
        """
        Create hashed password before storing
        """
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update password if it only part of the api
        """
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ["id", "organization_name"]


class InviteCodeSeriazlizer(serializers.ModelSerializer):

    class Meta:
        model = Invitecode
        fields = "__all__"