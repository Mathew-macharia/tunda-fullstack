# Generated by Django 5.1.3 on 2025-05-27 12:26

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0001_initial'),
        ('products', '0002_productlisting'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketPrice',
            fields=[
                ('price_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('average_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('max_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_date', models.DateField()),
                ('data_source', models.CharField(choices=[('platform', 'Platform'), ('market_survey', 'Market Survey'), ('government', 'Government')], default='platform', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='market_prices', to='locations.location')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='market_prices', to='products.product')),
            ],
            options={
                'verbose_name': 'Market Price',
                'verbose_name_plural': 'Market Prices',
                'ordering': ['-price_date'],
                'indexes': [models.Index(fields=['product', 'price_date'], name='data_insigh_product_ab8be2_idx'), models.Index(fields=['location'], name='data_insigh_locatio_9002ad_idx'), models.Index(fields=['data_source'], name='data_insigh_data_so_ab0c10_idx')],
                'constraints': [models.UniqueConstraint(fields=('product', 'location', 'price_date'), name='unique_price_record')],
            },
        ),
        migrations.CreateModel(
            name='WeatherAlert',
            fields=[
                ('alert_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('alert_type', models.CharField(choices=[('rain', 'Rain'), ('drought', 'Drought'), ('frost', 'Frost'), ('hail', 'Hail'), ('wind', 'Wind'), ('flood', 'Flood')], max_length=10)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], max_length=10)),
                ('alert_message', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weather_alerts', to='locations.location')),
            ],
            options={
                'verbose_name': 'Weather Alert',
                'verbose_name_plural': 'Weather Alerts',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['location', 'start_date'], name='data_insigh_locatio_6a9aa4_idx'), models.Index(fields=['alert_type'], name='data_insigh_alert_t_526cbe_idx'), models.Index(fields=['is_active'], name='data_insigh_is_acti_6395c2_idx')],
            },
        ),
    ]
