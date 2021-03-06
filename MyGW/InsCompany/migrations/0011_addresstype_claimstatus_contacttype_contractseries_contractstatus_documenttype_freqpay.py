# Generated by Django 2.1.7 on 2019-04-06 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InsCompany', '0010_auto_20190406_1645'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tat_val', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ClaimStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tcs_val', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tct_val', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ContractSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tcs_val', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ContractStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tcs_val', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tdt_val', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FreqPay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tfp_val', models.CharField(max_length=50)),
            ],
        ),
    ]
