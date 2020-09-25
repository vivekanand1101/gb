import django.db.models.deletion

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0004_auto_20200924_1400"),
    ]

    operations = [
        migrations.RemoveField(model_name="customeraccount", name="user",),
        migrations.AddField(
            model_name="customeraccount",
            name="customer",
            field=models.ForeignKey(
                default=None, on_delete=django.db.models.deletion.CASCADE, to="src.Customer",
            ),
            preserve_default=False,
        ),
    ]
