# Generated by Django 3.0.7 on 2020-11-07 06:28
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0002_receipt"),
    ]

    operations = [
        migrations.AddField(
            model_name="iteration",
            name="return_amount",
            field=models.IntegerField(default=5000),
            preserve_default=False,
        ),
    ]