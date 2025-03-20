# Generated by Django 5.1.7 on 2025-03-20 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0002_lastprocessed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='about',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
