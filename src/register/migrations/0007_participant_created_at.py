# Generated by Django 4.2.13 on 2024-06-05 11:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0006_remove_participant_email_participant_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='created_at',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
