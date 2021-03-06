# Generated by Django 3.1 on 2020-08-16 18:19

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200816_2340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='favourite_genres',
        ),
        migrations.CreateModel(
            name='movie',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('genres', models.CharField(max_length=255)),
                ('collection_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.collection')),
            ],
        ),
    ]
