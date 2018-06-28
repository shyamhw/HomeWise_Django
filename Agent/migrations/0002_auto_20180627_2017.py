# Generated by Django 2.0.5 on 2018-06-27 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Agent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.PositiveSmallIntegerField(choices=[(1, 'agent'), (2, 'client'), (3, 'vendor')], primary_key=True, serialize=False)),
            ],
        ),
        migrations.AlterModelManagers(
            name='agent',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='agent',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='agent',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='agent',
            name='username',
        ),
        migrations.AddField(
            model_name='user',
            name='agent_profile',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='Agent.Agent'),
        ),
        migrations.AddField(
            model_name='user',
            name='temp_password',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='agent',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(to='Agent.Role'),
        ),
    ]
