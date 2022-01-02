from django.db import models
from collectionfield.models import CollectionField
from django.core.files import File
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.safestring import mark_safe
from decimal import Decimal
from time import time


def problem_directory_upload(instance, filename):
    problem_title = instance.title.replace(' ', '')
    filename = filename.replace(' ','')
    return 'file/problem_{0}/{1}/{2}'.format(problem_title, time() , filename)


def testcase_directory_upload(instance, filename):
    problem_title = instance.problem.title.replace(' ', '')
    filename = filename.replace(' ','')
    return 'file/testcase_{0}/{1}'.format(problem_title+"_"+str(instance.problem.id), filename)


def submit_directory_upload(instance, filename):
    problem_title = instance.problem.title.replace(' ', '')
    filename = filename.replace(' ','')
    return 'file/user_{0}/{1}/{2}/{3}'.format(instance.user.id, problem_title, time() , filename)


def user_output_directory_upload(instance, filename):
    problem_title = instance.submit.problem.title.replace(' ', '')
    testcase_title = instance.test_case.name.replace(' ', '')
    filename = filename.replace(' ','')
    return 'file/user_{0}/{1}/{2}_{3}/{4}'.format(instance.user.id, problem_title, testcase_title, time() , filename)

# Create your models here.


class Campus(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='', blank=True)
    country = models.CharField(max_length=200, choices=(('Ethiopia', 'Ethiopia'), ('Ertirea', 'Ertirea')))
    flag = models.ImageField(upload_to='')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'country')

    def logo_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.logo.url)

    logo_tag.short_description = 'Logo'
    logo_tag.allow_tags = True

    def flag_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.flag.url)

    flag_tag.short_description = 'Flag'
    flag_tag.allow_tags = True


class User(models.Model):
    name = models.CharField(max_length=200, help_text='Enter user Name')
    middle_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{10,15}$',
        message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed'
    )
    phone = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    email = models.EmailField()
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    password = models.CharField(validators=[password_regex], max_length=1024)
    sex = models.CharField(max_length=200, choices=(('male', 'male'), ('female', 'female')))
    photo = models.ImageField(blank=True, upload_to='', default='null.png')
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, blank=True)
    register_date = models.DateField()

    def __str__(self):
        return self.name + ' ' + self.middle_name

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.photo.url)

    image_tag.short_description = 'Photo'
    image_tag.allow_tags = True


class Admin(models.Model):
    name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{10,15}$',
        message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed'
    )
    phone = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    email = models.EmailField()
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    password = models.CharField(validators=[password_regex], max_length=1024)
    sex = models.CharField(max_length=200, choices=(('male', 'male'), ('female', 'female')))
    photo = models.ImageField(blank=True, upload_to='', default='null.png')
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    register_date = models.DateField()

    def __str__(self):
        return self.name + ' ' + self.middle_name

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.photo.url)

    image_tag.short_description = 'Photo'
    image_tag.allow_tags = True


class Problem(models.Model):
    
    title = models.CharField(max_length=200)
    short_name = models.CharField(max_length=10)
    pdf = models.FileField(upload_to=problem_directory_upload, unique=True)
    point = models.DecimalField(default=1.0, decimal_places=2, max_digits=10,
                                validators=[MinValueValidator(Decimal('0.01'))])
    time_limit = models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal('0.01'))],
                                     help_text='enter time limit in second')
    memory_limit = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10,
                                       validators=[MinValueValidator(Decimal('0.01'))],
                                       help_text='Enter memory limit in mega bytes')
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    register_date = models.DateTimeField()

    def __str__(self):
        return self.title


class TestCase(models.Model):
    
    name = models.CharField(max_length=200)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input = models.FileField(upload_to=testcase_directory_upload)
    output = models.FileField(upload_to=testcase_directory_upload)

    class Meta:
        unique_together = ('problem', 'input', 'output')

    def __str__(self):
        return self.problem.title + ' test case ' + self.name


class Contest(models.Model):
    title = models.CharField(max_length=200)
    active_time = models.DateTimeField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    frozen_time = models.DateTimeField(blank=True, null=True)
    unfrozen_time = models.DateTimeField(blank=True, null=True)
    deactivate_time = models.DateTimeField(blank=True, null=True)
    problem = models.ManyToManyField(Problem)
    user = models.ManyToManyField(User)
    photo = models.ImageField(blank=True, upload_to='', default='icpc.png')
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    enable = models.CharField(max_length=200, choices=(('yes', 'yes'), ('no', 'no')), default='yes')
    register_date = models.DateTimeField()
    # limit_choices_to={'campus': 'astu'}

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.photo.url)

    image_tag.short_description = 'Photo'
    image_tag.allow_tags = True


class Submit(models.Model):

    submit_answer = models.FileField(upload_to=submit_directory_upload)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    result = models.CharField(max_length=200,
                              choices=(('Correct', 'Correct'), ('Time Limit Exceeded', 'Time Limit Exceeded'),
                                       ('Wrong Answer', 'Wrong Answer'), ('Compiler Error', 'Compiler Error'),
                                       ('Memory Limit Exceeded', 'Memory Limit Exceeded'),
                                       ('Run Time Error', 'Run Time Error'), ('No Output', 'No Output')
                                       )
                              )
    language = models.CharField(max_length=200, choices=(('C', 'C'), ('C++', 'C++'), ('Python2', 'Python2'),
                                                         ('Python3', 'Python3'), ('Java', 'Java')))
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    submit_time = models.DateTimeField()
    '''
    class Meta:
        unique_together = ('user', 'problem', 'submit_answer')
    '''

    def __str__(self):
        return self.problem.title + ' by ' + self.user.name


class SubmitOutput(models.Model):
    
    output = models.FileField(upload_to=user_output_directory_upload)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    submit = models.ForeignKey(Submit, on_delete=models.CASCADE)
    result = models.CharField(max_length=200,
                              choices=(('Correct', 'Correct'), ('Time Limit Exceeded', 'Time Limit Exceeded'),
                                       ('Wrong Answer', 'Wrong Answer'), ('Compiler Error', 'Compiler Error'),
                                       ('Memory Limit Exceeded', 'Memory Limit Exceeded'),
                                       ('Run Time Error', 'Run Time Error'), ('No Output', 'No Output')
                                       )
                              )

    class Meta:
        unique_together = ('test_case', 'output')

    def __str__(self):
        return self.test_case.problem.short_name + ' test case ' + self.test_case.name + ' output by '+self.user.name


