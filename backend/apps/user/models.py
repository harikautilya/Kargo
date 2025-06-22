from django.db import models

class Organization(models.Model):
    """
    Model class for organization
    """

    id = models.AutoField(primary_key=True)
    organization_name = models.CharField(max_length=1024)


class User(models.Model):
    """
    Model class for User
    """

    id = models.AutoField(primary_key=True)
    display_name = models.CharField(max_length=225)
    username = models.CharField(max_length=48, unique=True)
    password = models.CharField(max_length=255) # Stored as hash from django.contrib.auth.hashers import make_password 
    org = models.ForeignKey(Organization, on_delete=models.DO_NOTHING)

class Invitecode(models.Model):
    """
    Invite codes
    """
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name="created_user")
    used_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="used_user", null=True, blank=True),
    expiry_at  = models.DateTimeField()
    expired = models.BooleanField(default=False)