# Generated by Django 4.2.13 on 2024-05-27 12:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('register', '0005_alter_participant_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='email',
        ),
        migrations.AddField(
            model_name='participant',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
