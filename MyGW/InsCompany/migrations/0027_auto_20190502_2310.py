# Generated by Django 2.1.7 on 2019-05-02 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InsCompany', '0026_risk_rsk_ins_proportion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='tco_end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='tco_pre_end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='tco_start_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='dealer',
            name='tde_end',
            field=models.DateField(null=True),
        ),
    ]
