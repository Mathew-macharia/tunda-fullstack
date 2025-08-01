# Generated by Django 4.2.10 on 2025-07-06 00:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_paymentsession_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenttransaction',
            name='payment_session',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions',
                to='payments.paymentsession'
            ),
        ),
        migrations.AddIndex(
            model_name='paymenttransaction',
            index=models.Index(
                fields=['payment_session'],
                name='payment_session_idx'
            ),
        ),
    ]
