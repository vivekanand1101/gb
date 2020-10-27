# Generated by Django 3.0.7 on 2020-10-27 06:52
import django.db.models.deletion

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0012_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="address",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="src.Address"
            ),
        ),
    ]
