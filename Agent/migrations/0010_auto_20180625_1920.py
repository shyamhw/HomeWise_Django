# Generated by Django 2.0.5 on 2018-06-25 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agent', '0009_auto_20180625_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]