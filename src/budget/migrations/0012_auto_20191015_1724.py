# Generated by Django 2.2.6 on 2019-10-15 15:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0011_auto_20191015_1718'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='application',
            index_together={('submitted', 'date')},
        ),
    ]
