# Generated by Django 2.1.7 on 2019-05-08 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InsCompany', '0030_workerphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='tco_sign_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='workerphoto',
            name='wp_photo',
            field=models.ImageField(upload_to='MyGW/InsCompany/media/worker_photos/'),
        ),
    ]
