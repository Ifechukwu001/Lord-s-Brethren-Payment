# Generated by Django 4.2.13 on 2024-05-18 15:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='reference',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
