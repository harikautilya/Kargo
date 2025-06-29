# Generated by Django 5.2.3 on 2025-06-18 07:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_user_username"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invitecode",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=10, unique=True)),
                ("expiry_at", models.DateTimeField()),
                ("expired", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="created_user",
                        to="user.user",
                    ),
                ),
            ],
        ),
    ]
