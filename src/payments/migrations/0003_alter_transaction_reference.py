# Generated by Django 4.2.13 on 2024-05-18 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_transaction_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='reference',
            field=models.CharField(default='<function uuid4 at 0x7c5e94f12e60>', max_length=100),
        ),
    ]
