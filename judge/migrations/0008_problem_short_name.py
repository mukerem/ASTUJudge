# Generated by Django 2.0.7 on 2018-12-09 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0007_submit_contest'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='short_name',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
    ]