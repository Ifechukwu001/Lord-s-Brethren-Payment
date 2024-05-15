# Generated by Django 4.2.13 on 2024-05-15 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0002_alter_participant_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='type',
        ),
        migrations.AddField(
            model_name='participant',
            name='category',
            field=models.CharField(choices=[('Invitee', 'Invitee'), ('Member', 'Member')], default='Invitee', max_length=10),
        ),
    ]
