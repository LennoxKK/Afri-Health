# Generated by Django 5.1.4 on 2024-12-09 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_collection', '0002_user_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]