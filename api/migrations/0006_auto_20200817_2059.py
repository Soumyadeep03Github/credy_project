# Generated by Django 3.1 on 2020-08-17 15:29

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200817_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
