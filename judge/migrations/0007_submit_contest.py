# Generated by Django 2.0.7 on 2018-12-07 18:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0006_contest_enable'),
    ]

    operations = [
        migrations.AddField(
            model_name='submit',
            name='contest',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='judge.Contest'),
            preserve_default=False,
        ),
    ]
