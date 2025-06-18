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
