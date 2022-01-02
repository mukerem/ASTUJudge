# Generated by Django 2.0.7 on 2018-12-03 07:20

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import judge.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('middle_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('phone', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed', regex='^\\+?1?\\d{10,15}$')])),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(message='password must be at least 6 character', regex='^\\S{6,1024}')])),
                ('sex', models.CharField(choices=[('male', 'male'), ('female', 'female')], max_length=200)),
                ('photo', models.ImageField(blank=True, default='null.png', upload_to='')),
                ('register_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('logo', models.ImageField(blank=True, upload_to='')),
                ('country', models.CharField(choices=[('Ethiopia', 'Ethiopia'), ('Ertirea', 'Ertirea')], max_length=200)),
                ('flag', models.ImageField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('pdf', models.FileField(unique=True, upload_to=judge.models.problem_directory_upload)),
                ('point', models.DecimalField(decimal_places=2, default=1.0, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('time_limit', models.DecimalField(decimal_places=2, help_text='enter time limit in second', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('memory_limit', models.DecimalField(blank=True, decimal_places=2, help_text='Enter memory limit in mega bytes', max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('register_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Submit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submit_answer', models.FileField(upload_to=judge.models.submit_directory_upload)),
                ('result', models.CharField(choices=[('Correct', 'Correct'), ('Time Limit Exceeded', 'Time Limit Exceeded'), ('Wrong Answer', 'Wrong Answer'), ('Compiler Error', 'Compiler Error'), ('Memory Limit Exceeded', 'Memory Limit Exceeded'), ('Run Time Error', 'Run Time Error'), ('No Output', 'No Output')], max_length=200)),
                ('language', models.CharField(choices=[('C', 'C'), ('C++', 'C++'), ('Python2', 'Python2'), ('Python3', 'Python3'), ('Java', 'Java')], max_length=200)),
                ('submit_time', models.DateTimeField()),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='SubmitOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output', models.FileField(upload_to=judge.models.submit_directory_upload)),
                ('result', models.CharField(choices=[('Correct', 'Correct'), ('Time Limit Exceeded', 'Time Limit Exceeded'), ('Wrong Answer', 'Wrong Answer'), ('Compiler Error', 'Compiler Error'), ('Memory Limit Exceeded', 'Memory Limit Exceeded'), ('Run Time Error', 'Run Time Error'), ('No Output', 'No Output')], max_length=200)),
                ('submit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Submit')),
            ],
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('input', models.FileField(upload_to=judge.models.testcase_directory_upload)),
                ('output', models.FileField(upload_to=judge.models.testcase_directory_upload)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter user Name', max_length=200)),
                ('middle_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('phone', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed', regex='^\\+?1?\\d{10,15}$')])),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(message='password must be at least 6 character', regex='^\\S{6,1024}')])),
                ('sex', models.CharField(choices=[('male', 'male'), ('female', 'female')], max_length=200)),
                ('photo', models.ImageField(blank=True, default='null.png', upload_to='')),
                ('register_date', models.DateField()),
                ('campus', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='judge.Campus')),
            ],
        ),
        migrations.AddField(
            model_name='submitoutput',
            name='test_case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.TestCase'),
        ),
        migrations.AddField(
            model_name='submitoutput',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.User'),
        ),
        migrations.AddField(
            model_name='submit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.User'),
        ),
        migrations.AlterUniqueTogether(
            name='campus',
            unique_together={('name', 'country')},
        ),
        migrations.AddField(
            model_name='admin',
            name='campus',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='judge.Campus'),
        ),
        migrations.AlterUniqueTogether(
            name='testcase',
            unique_together={('problem', 'input', 'output')},
        ),
        migrations.AlterUniqueTogether(
            name='submitoutput',
            unique_together={('test_case', 'output')},
        ),
    ]
