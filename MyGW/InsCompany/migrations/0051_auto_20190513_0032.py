# Generated by Django 2.1.7 on 2019-05-12 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InsCompany', '0050_contractrisk_tcr_str_sum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='risk',
            name='rsk_ins_proportion',
            field=models.IntegerField(default=1),
        ),
    ]
