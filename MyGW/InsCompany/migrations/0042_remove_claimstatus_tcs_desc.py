# Generated by Django 2.1.7 on 2019-05-12 00:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('InsCompany', '0041_remove_contractstatus_tcs_desc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='claimstatus',
            name='tcs_desc',
        ),
    ]
