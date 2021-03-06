# Generated by Django 3.1.4 on 2020-12-06 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calories', '0004_auto_20201206_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bmi',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='bmr',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='exercise_level',
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='tdee',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
