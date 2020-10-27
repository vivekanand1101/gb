# Generated by Django 3.0.7 on 2020-10-27 05:54
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0010_loan_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="loan",
            name="status",
            field=models.CharField(
                choices=[("PENDING", "PENDING"), ("APPROVED", "APPROVED")],
                default="APPROVED",
                max_length=20,
            ),
        ),
    ]