# Generated by Django 4.2.13 on 2024-05-25 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_transaction_for_ticket_alter_transaction_reference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='for_ticket',
        ),
    ]
