# Generated by Django 2.0.5 on 2018-06-26 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agent', '0010_auto_20180625_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='company_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
