# Generated by Django 2.0.5 on 2018-06-01 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agent', '0003_auto_20180601_0637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
