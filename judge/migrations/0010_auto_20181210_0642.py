# Generated by Django 2.0.7 on 2018-12-10 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0009_auto_20181209_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submit',
            name='result',
            field=models.CharField(choices=[('Correct', 'Correct'), ('Time Limit Exceeded', 'Time Limit Exceeded'), ('Wrong Answer', 'Wrong Answer'), ('Compiler Error', 'Compiler Error'), ('Memory Limit Exceeded', 'Memory Limit Exceeded'), ('Run Time Error', 'Run Time Error'), ('No Output', 'No Output')], max_length=200),
        ),
    ]