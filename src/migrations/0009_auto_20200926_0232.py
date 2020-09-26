# Generated by Django 3.0.7 on 2020-09-26 02:32
import django.db.models.deletion

from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("src", "0008_auto_20200925_0118"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountDeposit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("date", models.DateField()),
                ("amount", models.IntegerField()),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deposits",
                        to="src.Account",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accountdeposit_createdby",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accountdeposit_modifiedby",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Account Deposit",
                "verbose_name_plural": "Account Deposits",
                "db_table": "account_deposits",
            },
        ),
        migrations.DeleteModel(name="IterationDeposit",),
    ]
