# Generated by Django 2.0.5 on 2018-07-02 14:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mls_region', models.CharField(blank=True, max_length=254, null=True)),
                ('mls_id', models.CharField(blank=True, max_length=100, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('client_type', models.CharField(blank=True, max_length=1, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=30, null=True)),
                ('state', models.CharField(blank=True, max_length=2, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=5, null=True)),
                ('est_price', models.FloatField(blank=True, max_length=20, null=True, verbose_name='est price')),
                ('commission', models.FloatField(blank=True, max_length=3, null=True, verbose_name='commission')),
                ('commission_val', models.FloatField(blank=True, max_length=20, null=True, verbose_name='commission val')),
                ('total_steps', models.IntegerField(blank=True, null=True, verbose_name='total steps')),
                ('steps_complete', models.IntegerField(blank=True, null=True, verbose_name='steps complete')),
                ('steps_percentage', models.FloatField(blank=True, max_length=20, null=True, verbose_name='steps_percentage')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Agent.Agent')),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='MLSRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(blank=True, max_length=30, null=True)),
                ('long_name', models.CharField(blank=True, max_length=100, null=True)),
                ('office_location', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.PositiveSmallIntegerField(choices=[(1, 'agent'), (2, 'client'), (3, 'vendor')], primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.IntegerField(blank=True, null=True, verbose_name='ordering')),
                ('name', models.CharField(blank=True, max_length=60, null=True)),
                ('complete', models.BooleanField(default=False)),
                ('agent_email', models.CharField(blank=True, max_length=254, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Agent.Client')),
            ],
            options={
                'ordering': ('date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('company_name', models.CharField(blank=True, max_length=150, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.CharField(blank=True, max_length=254, null=True)),
                ('long_description', models.CharField(blank=True, max_length=300, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('yelp_link', models.CharField(blank=True, max_length=200, null=True)),
                ('facebook_link', models.CharField(blank=True, max_length=200, null=True)),
                ('website_link', models.CharField(blank=True, max_length=200, null=True)),
                ('tags', models.ManyToManyField(to='Agent.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='VendorRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('temp_password', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='vendor',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vendor',
            name='vendor_region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Agent.VendorRegion'),
        ),
        migrations.AddField(
            model_name='step',
            name='tags',
            field=models.ManyToManyField(to='Agent.Tag'),
        ),
        migrations.AddField(
            model_name='mlsregion',
            name='vendor_region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Agent.VendorRegion'),
        ),
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agent',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='agent',
            unique_together={('mls_region', 'mls_id')},
        ),
    ]
