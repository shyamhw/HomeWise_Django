# Generated by Django 2.0.5 on 2018-07-03 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agent', '0002_auto_20180702_2122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='tags',
            field=models.ManyToManyField(blank=True, to='Agent.Tag'),
        ),
    ]