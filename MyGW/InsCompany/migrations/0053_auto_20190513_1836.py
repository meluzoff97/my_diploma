# Generated by Django 2.1.7 on 2019-05-13 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InsCompany', '0052_auto_20190513_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='doc_issue_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='doc_issue_org',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='doc_number',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='doc_series',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
