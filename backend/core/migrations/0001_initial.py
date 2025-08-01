# Generated by Django 5.1.3 on 2025-05-27 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('setting_id', models.AutoField(primary_key=True, serialize=False)),
                ('setting_key', models.CharField(max_length=100, unique=True)),
                ('setting_value', models.TextField()),
                ('setting_type', models.CharField(choices=[('string', 'String'), ('number', 'Number'), ('boolean', 'Boolean'), ('json', 'JSON')], default='string', max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'System Setting',
                'verbose_name_plural': 'System Settings',
                'db_table': 'System_Settings',
                'ordering': ['setting_key'],
            },
        ),
    ]
