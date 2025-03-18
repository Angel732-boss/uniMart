# Generated by Django 5.1.7 on 2025-03-18 08:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0003_alter_post_slug'),
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(limit_choices_to={'service_type'}, on_delete=django.db.models.deletion.PROTECT, related_name='posts', to='utils.category'),
        ),
    ]
