# Generated by Django 2.0.7 on 2018-12-05 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0003_auto_20181205_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='register_date',
            field=models.DateTimeField(),
        ),
    ]
