# Generated by Django 2.1.7 on 2019-05-10 15:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('InsCompany', '0034_auto_20190509_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='dealer',
            name='tde_user_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
