# Generated by Django 3.1.4 on 2020-12-06 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calories', '0003_auto_20201206_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='age',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='sex',
            field=models.CharField(max_length=6, null=True),
        ),
    ]