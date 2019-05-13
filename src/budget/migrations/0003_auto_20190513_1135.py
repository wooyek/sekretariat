# Generated by Django 2.2.1 on 2019-05-13 09:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_auto_20190513_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='manager',
            field=models.ForeignKey(limit_choices_to=models.Q(groups__name='Managers'), on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]