# Generated by Django 2.1.7 on 2019-05-12 00:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('InsCompany', '0042_remove_claimstatus_tcs_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insevent',
            name='tiv_tcs_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='InsCompany.ClaimStatus'),
        ),
    ]