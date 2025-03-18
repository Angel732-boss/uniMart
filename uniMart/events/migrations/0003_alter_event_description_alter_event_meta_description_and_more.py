# Generated by Django 5.1.7 on 2025-03-18 03:37

import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_event_capacity_event_category_alter_event_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='meta_description',
            field=models.CharField(blank=True, help_text='Content for description meta tag', max_length=255, null=True, verbose_name='Meta Description'),
        ),
        migrations.AlterField(
            model_name='event',
            name='meta_keywords',
            field=models.CharField(blank=True, help_text='Comma delimited set of SEO keywords for meta tag', max_length=255, null=True, verbose_name='Meta Keywords'),
        ),
        migrations.AlterField(
            model_name='event',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True),
        ),
    ]
