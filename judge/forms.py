from django import forms
from django.forms import ChoiceField
from .models import User, Admin, Campus, SubmitOutput, Problem, Submit, TestCase, Contest
from django.core.validators import RegexValidator
from datetime import datetime
import time, pytz


class UserRegister(forms.ModelForm):
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    user_password = forms.CharField(
        validators=[password_regex],
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Enter your password minimum 6 character',
        label='Password'
    )
    confirm_password = forms.CharField(
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Confirm your password'
    )

    class Meta:
        model = User
        fields = ['name', 'middle_name', 'last_name', 'phone', 'email', 'sex', 'user_password',
                  'confirm_password',  'photo', 'campus']
        help_texts = {
            'name': "* Enter user first name",
            'middle_name': "* Enter user middle name",
            'last_name': "* Enter user last name",
            'phone': "Enter user phone number",
            'sex': "Enter user gender",
            'email': "* Enter user email (if any)",
            'campus': "Enter user current campus",
            'photo': "Enter user photo (if any)",

        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        middle_name = cleaned_data.get('middle_name')
        last_name = cleaned_data.get('last_name')
        user_password = cleaned_data.get('user_password')
        confirm = cleaned_data.get('confirm_password')
        sex = cleaned_data.get('sex')
        email = cleaned_data.get('email')

        if (not name) or (not middle_name) or (not last_name) or (not sex) or (not user_password) or (not confirm):
            raise forms.ValidationError("Please correct the errors below.")

        if user_password and confirm:
            if user_password != confirm:
                raise forms.ValidationError("password is not confirmed")
        try:
            User.objects.get(email=email)
            raise forms.ValidationError("User with this Email already exists.")
        except User.DoesNotExist:
            try:
                Admin.objects.get(email=email)
                raise forms.ValidationError("Admin with this Email already exists.")
            except Admin.DoesNotExist:
                pass
        return cleaned_data


class AdminRegister(forms.ModelForm):
    class UserRegister(forms.ModelForm):
        password_regex = RegexValidator(
            regex=r'^\S{6,1024}',
            message='password must be at least 6 character'
        )
        user_password = forms.CharField(
            validators=[password_regex],
            max_length=1024,
            widget=forms.PasswordInput(),
            help_text='*Enter your password minimum 6 character',
            label='Password'
        )
        confirm_password = forms.CharField(
            max_length=1024,
            widget=forms.PasswordInput(),
            help_text='*Confirm your password'
        )

        class Meta:
            model = Admin
            fields = ['name', 'middle_name', 'last_name', 'phone', 'email', 'sex', 'user_password',
                      'confirm_password', 'photo', 'campus']
            help_texts = {
                'name': "* Enter user first name",
                'middle_name': "* Enter user middle name",
                'last_name': "* Enter user last name",
                'phone': "Enter user phone number",
                'sex': "Enter user gender",
                'email': "* Enter user email (if any)",
                'campus': "Enter user current campus",
                'photo': "Enter user photo (if any)",

            }

        def clean(self):
            cleaned_data = super().clean()
            name = cleaned_data.get('name')
            middle_name = cleaned_data.get('middle_name')
            last_name = cleaned_data.get('last_name')
            user_password = cleaned_data.get('user_password')
            confirm = cleaned_data.get('confirm_password')
            sex = cleaned_data.get('sex')
            email = cleaned_data.get('email')

            if (not name) or (not middle_name) or (not last_name) or (not sex) or (not user_password) or (not confirm):
                raise forms.ValidationError("Please correct the errors below.")

            if user_password and confirm:
                if user_password != confirm:
                    raise forms.ValidationError("password is not confirmed")
            try:
                User.objects.get(email=email)
                raise forms.ValidationError("User with this Email already exists.")
            except User.DoesNotExist:
                try:
                    Admin.objects.get(email=email)
                    raise forms.ValidationError("Admin with this Email already exists.")
                except Admin.DoesNotExist:
                    pass
            return cleaned_data


class Login(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(),
    )
    password = forms.CharField(
        max_length=1024,
        widget=forms.PasswordInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        email = cleaned_data.get('email')

        if (not password) or (not email):
            raise forms.ValidationError("Please correct the errors below.")

        if password and email:
            try:
                user = User.objects.get(email=email)
                _password = user.password

            except User.DoesNotExist:
                try:
                    admin = Admin.objects.get(email=email)
                    _password = admin.password

                except Admin.DoesNotExist:
                    raise forms.ValidationError("Please enter the correct email and password account.Note that "
                                                "both fields may be case-sensitive.")

            if password == _password:
                return
            else:
                raise forms.ValidationError("Please enter the correct email and password account. "
                                            "Note that both fields may be case-sensitive. ")

        return cleaned_data


class ForgotPassword(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if not email:
            raise forms.ValidationError("Please correct the errors below.")

        if email:
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                try:
                    Admin.objects.get(email=email)
                except Admin.DoesNotExist:
                    raise forms.ValidationError("Please enter the correct email.")

        return cleaned_data


class EditUserProfile(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user_email = kwargs.pop('user_email')

        super(EditUserProfile, self).__init__(*args, **kwargs)
        self.options = [['male', 'male'], ['female', 'female']]
        user = User.objects.get(email=self.user_email)
        self.email = user.email

        self.campus_options = [(i.id, i.name) for i in Campus.objects.all().order_by('name')]
        self.campus_options.insert(0, (None, '------------------'))
        self.initial['campus'] = user.campus.id
        self.initial['sex'] = user.sex
        self.fields['name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=user.name,
        )
        self.fields['middle_name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=user.middle_name,
        )
        self.fields['last_name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=user.last_name,
        )
        phone_regex = RegexValidator(
            regex=r'^\+?1?\d{10,15}$',
            message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed'
        )
        self.fields['phone'] = forms.CharField(
            validators=[phone_regex],
            max_length=15,
            widget=forms.TextInput(),
            initial=user.phone,
        )

        self.fields['email'] = forms.EmailField(
            max_length=254,
            widget=forms.TextInput(),
            initial=user.email,
        )
        self.fields['photo'] = forms.ImageField(
            required=False,
            initial="Images/" + str(user.photo),
        )
        self.fields['sex'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=self.options,
        )

        self.fields['campus'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=self.campus_options,
        )

        self.fields['registered_date'] = forms.DateField(
            widget=forms.DateInput(),
            initial=user.register_date,
            disabled=True,
        )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        middle_name = cleaned_data.get('middle_name')
        last_name = cleaned_data.get('last_name')
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        sex = cleaned_data.get('sex')
        campus = cleaned_data.get('campus')
        if (not name) or (not middle_name) or (not last_name) or (not phone) or (not email) or (not sex) or (not campus):
            raise forms.ValidationError("Please correct the errors below.")

        if email != self.email:
            try:
                Admin.objects.get(email=email)
                raise forms.ValidationError("Admin with this Email already exists.")
            except Admin.DoesNotExist:
                try:
                    User.objects.get(email=email)
                    raise forms.ValidationError("User with this Email already exists.")
                except User.DoesNotExist:
                    pass
        return cleaned_data


class EditAdminProfile(forms.Form):

    def __init__(self, *args, **kwargs):
        self.admin_email = kwargs.pop('admin_email')

        super(EditAdminProfile, self).__init__(*args, **kwargs)
        self.options = [['male', 'male'], ['female', 'female']]
        admin = Admin.objects.get(email=self.admin_email)
        self.email = admin.email

        self.campus_options = [(i.id, i.name) for i in Campus.objects.all().order_by('name')]
        self.campus_options.insert(0, (None, '------------------'))
        self.initial['campus'] = admin.campus.id
        self.initial['sex'] = admin.sex
        self.fields['name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=admin.name,
        )
        self.fields['middle_name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=admin.middle_name,
        )
        self.fields['last_name'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=admin.last_name,
        )
        phone_regex = RegexValidator(
            regex=r'^\+?1?\d{10,15}$',
            message='Phone number must be entered in the format : 0987654321 or +251987654321 up to 15 digits allowed'
        )
        self.fields['phone'] = forms.CharField(
            validators=[phone_regex],
            max_length=15,
            widget=forms.TextInput(),
            initial=admin.phone,
        )

        self.fields['email'] = forms.EmailField(
            max_length=254,
            widget=forms.TextInput(),
            initial=admin.email,
        )
        self.fields['photo'] = forms.ImageField(
            required=False,
            initial="Images/" + str(admin.photo),
        )
        self.fields['sex'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=self.options,
        )

        self.fields['campus'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=self.campus_options,
        )

        self.fields['registered_date'] = forms.DateField(
            widget=forms.DateInput(),
            initial=admin.register_date,
            disabled=True,
        )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        middle_name = cleaned_data.get('middle_name')
        last_name = cleaned_data.get('last_name')
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        sex = cleaned_data.get('sex')
        campus = cleaned_data.get('campus')
        if (not name) or (not middle_name) or (not last_name) or (not phone) or (not email) or (not sex) or (not campus):
            raise forms.ValidationError("Please correct the errors below.")

        if email != self.email:
            try:
                Admin.objects.get(email=email)
                raise forms.ValidationError("Admin with this Email already exists.")
            except Admin.DoesNotExist:
                try:
                    User.objects.get(email=email)
                    raise forms.ValidationError("User with this Email already exists.")
                except User.DoesNotExist:
                    pass
        return cleaned_data


class AddUser(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'middle_name', 'last_name', 'phone', 'email', 'sex', 'photo']
        help_texts = {
            'name': "* Enter user first name",
            'middle_name': "* Enter user middle name",
            'last_name': "* Enter user last name",
            'phone': "Enter user phone number",
            'sex': "Enter user gender",
            'email': "* Enter user email (if any)",
            'photo': "Enter user photo (if any)",

        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        middle_name = cleaned_data.get('middle_name')
        last_name = cleaned_data.get('last_name')
        sex = cleaned_data.get('sex')
        email = cleaned_data.get('email')

        if (not name) or (not middle_name) or (not last_name) or (not sex) :
            raise forms.ValidationError("Please correct the errors below.")

        try:
            User.objects.get(email=email)
            raise forms.ValidationError("User with this Email already exists.")
        except User.DoesNotExist:
            try:
                Admin.objects.get(email=email)
                raise forms.ValidationError("Admin with this Email already exists.")
            except Admin.DoesNotExist:
                pass
        return cleaned_data


class ChangePassword(forms.Form):
    def __init__(self, *args, **kwargs):
        self.password = kwargs.pop('key')

        super(ChangePassword, self).__init__(*args, **kwargs)

    old_password = forms.CharField(
        max_length=1024,
        widget=forms.PasswordInput(),
    )
    password_regex = RegexValidator(
        regex=r'^\S{6,1024}',
        message='password must be at least 6 character'
    )
    new_password = forms.CharField(
        validators=[password_regex],
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Enter your new password minimum 6 character'
    )
    confirm = forms.CharField(
        label='Confirm Password',
        max_length=1024,
        widget=forms.PasswordInput(),
        help_text='*Enter your new password again'
    )

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm')
        if (not old_password) or (not new_password) or (not confirm_password):
            raise forms.ValidationError("Please correct the errors below.")

        if old_password == self.password:
            if new_password:
                if new_password == confirm_password:
                    return
                else:
                    raise forms.ValidationError("password is not confirmed")
        else:
            raise forms.ValidationError("Please enter the correct old password. ")

        return cleaned_data


class SubmitAnswer(forms.Form):
    def __init__(self, *args, **kwargs):
        self.current_contest_id = kwargs.pop('current_contest_id')

        super(SubmitAnswer, self).__init__(*args, **kwargs)
        current_contest = Contest.objects.get(pk=self.current_contest_id)

        language_options = [(None, '--------------'), ('C', 'C'), ('C++', 'C++'), ('Python2', 'Python2'),
                            ('Python3', 'Python3'), ('Java', 'Java')]
        contest_problems = current_contest.problem.all()
        question_options = [(i.id, i) for i in contest_problems]
        question_options = sorted(question_options, key=lambda x: x[1].title.lower())
        question_options.insert(0, (None, '--------------'))
        self.fields['file'] = forms.FileField(
            help_text="* Choose your code."
        )
        self.fields['language'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=language_options,
            help_text="* Select programming language"
        )
        self.fields['problem'] = forms.ChoiceField(
            widget=forms.Select(),
            choices=question_options,
            help_text="* Select a problem"
        )

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        language = cleaned_data.get('language')
        problem = cleaned_data.get('problem')

        if (not file) or (not problem) or (not language):
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data


class AddProblem(forms.ModelForm):

    class Meta:
        model = Problem
        fields = ['title', 'pdf', 'time_limit', 'memory_limit', 'point']
        help_texts = {
            'title': "* Enter title of problem",
            'pdf': "* Choose problem pdf",
            'time_limit': "*Enter time limit of the problem in second",
            'memory_limit': "Enter memory limit of the problem in megabytes",
            'point': "*Enter point for the problem",
        }

    def clean(self):
        cleaned_data = super().clean()
        pdf = cleaned_data.get('pdf')
        title = cleaned_data.get('title')
        time_limit = cleaned_data.get('time_limit')
        point = cleaned_data.get('point')

        if (not pdf) or (not title) or (not time_limit)  or (not point):
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data


class EditProblem(forms.Form):

    def __init__(self, *args, **kwargs):
        self.problem_id = kwargs.pop('problem_id')

        super(EditProblem, self).__init__(*args, **kwargs)

        problem = Problem.objects.get(pk=self.problem_id)

        self.fields['title'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            initial=problem.title,
        )
        self.fields['time_limit'] = forms.DecimalField(
            widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            initial=problem.time_limit,
        )
        self.fields['memory_limit'] = forms.DecimalField(
            widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            initial=problem.memory_limit,
            required=False,
        )
        self.fields['point'] = forms.DecimalField(
            widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            initial=problem.point,
        )
        self.fields['pdf'] = forms.FileField(
            initial="Images/" + str(problem.pdf),
        )
        self.fields['registered_date'] = forms.DateField(
            widget=forms.DateInput(),
            initial=problem.register_date,
            disabled=True,
        )


    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        time_limit = cleaned_data.get('time_limit')
        point = cleaned_data.get('point')
        pdf = cleaned_data.get('pdf')
        print(pdf)
        if (not title) or (not time_limit) or (not point) or (not pdf):
            raise forms.ValidationError("Please correct the errors below.")


        return cleaned_data


class AddSample(forms.ModelForm):
    '''
    sample_input = forms.FileField(
        help_text="* Choose sample input."
    )
    sample_output = forms.FileField(
        help_text="* Choose sample output."
    )
    '''
    class Meta:
        model = TestCase
        fields = ['input', 'output']
        help_texts = {

            'sample_input': "* Choose sample input",
            'sample_output': "* Choose sample output",
        }

    def clean(self):
        cleaned_data = super().clean()

        sample_input = cleaned_data.get('input')
        sample_output = cleaned_data.get('input')

        if (not sample_input) or (not sample_output):
            raise forms.ValidationError("Please correct the errors below.")

        return cleaned_data


class ContestRegister(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.campus = kwargs.pop('campus')

        super(ContestRegister, self).__init__(*args, **kwargs)

        self.fields['problem'] = forms.ModelMultipleChoiceField(
            queryset=Problem.objects.filter(campus=self.campus),
            widget=forms.CheckboxSelectMultiple(),
        )

    '''
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )
    problems = forms.ModelMultipleChoiceField(
        queryset=Problem.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )
    '''
    # problem = forms.ModelMultipleChoiceField()

    class Meta:
        model = Contest
        fields = ['title', 'active_time', 'start_time', 'end_time', 'frozen_time', 'unfrozen_time', 'deactivate_time',
                  'problem', 'user', 'photo']
        help_texts = {
            'title': "* title of contest",
            'active_time': "* time of activate",
            'start_time': "* time of the contest begin in YYYY-MM-DD HH:MM:SS format",
            'end_time': "* time of contest end",
            'frozen_time': "time of frozen of scoreboard",
            'unfrozen_time': "unfrozen time of the scoreboard",
            'deactivate_time': "time of deactivate of the contest",
            'photo': "contest image (if any)",
            'problem': '* contest problems select any of them.',
            'user': '* select participants'

        }
        widgets = {
            'problem': forms.CheckboxSelectMultiple(),
            'user': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        active_time = cleaned_data.get('active_time')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        frozen_time = cleaned_data.get('frozen_time')
        unfrozen_time = cleaned_data.get('unfrozen_time')
        deactivate_time = cleaned_data.get('deactivate_time')
        problem = cleaned_data.get('problem')
        user = cleaned_data.get('user')

        if (not title) or (not active_time) or (not start_time) or (not end_time) or (not problem) or (not user):
            raise forms.ValidationError("Please correct the errors below.")

        utc = pytz.UTC
        now = utc.localize(datetime.now())
        if start_time < now:
            raise forms.ValidationError("start time must be after now( " + str(datetime.now())+' )')
        if active_time > start_time:
            raise forms.ValidationError("Active time must be before start time.")
        if end_time < start_time:
            raise forms.ValidationError("Start time must be before end time.")
        if frozen_time and frozen_time > end_time:
            raise forms.ValidationError("Frozen time must be before end time.")
        if unfrozen_time and unfrozen_time < end_time:
            raise forms.ValidationError("Unfrozen time must be after end time.")
        if deactivate_time and deactivate_time < end_time:
            raise forms.ValidationError("Deactivate time must be after end time.")
        return cleaned_data


class EditContest(forms.Form):

    def __init__(self, *args, **kwargs):
        self.contest_id = kwargs.pop('contest_id')

        super(EditContest, self).__init__(*args, **kwargs)
        contest = Contest.objects.get(pk=self.contest_id)

        self.fields['title'] = forms.CharField(
            max_length=200,
            widget=forms.TextInput(),
            help_text="* Enter title of the event",
        )
        self.fields['active_time'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            help_text="* time of activate",
            initial=contest.active_time,
        )
        self.fields['start_time'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            help_text="* time of the contest begin in YYYY-MM-DD HH:MM:SS format",
            initial=contest.start_time,
        )

        self.fields['end_time'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            help_text="* time of contest end.",
            initial=contest.end_time,
        )
        self.fields['frozen_time'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            required=False,
            help_text="time of frozen of scoreboard",
            initial=contest.frozen_time,
        )
        self.fields['unfrozen_time'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            required=False,
            help_text="time of unfrozen of scoreboard",
            initial=contest.unfrozen_time,
        )
        self.fields['deactivate_time'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            required=False,
            help_text="time of deactivate of the contest",
            initial=contest.deactivate_time,
        )

        self.fields['problem'] = forms.ModelMultipleChoiceField(
            queryset=Problem.objects.filter(campus=contest.campus),
            widget=forms.CheckboxSelectMultiple(),
            # initial=contest.problem
        )
        self.fields['user'] = forms.ModelMultipleChoiceField(
            queryset=User.objects.filter(campus=contest.campus),
            widget=forms.CheckboxSelectMultiple(),
            initial=contest.user.all()
        )
        self.fields['photo'] = forms.ImageField(
            required=False,
            initial="Images/" + str(contest.photo),
        )
        self.fields['registered_date'] = forms.DateTimeField(
            widget=forms.DateTimeInput(),
            initial=contest.register_date,
            disabled=True,
        )

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        active_time = cleaned_data.get('active_time')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        frozen_time = cleaned_data.get('frozen_time')
        unfrozen_time = cleaned_data.get('unfrozen_time')
        deactivate_time = cleaned_data.get('deactivate_time')
        problem = cleaned_data.get('problem')
        user = cleaned_data.get('user')

        if (not title) or (not active_time) or (not start_time) or (not end_time) or (not problem) or (not user):
            raise forms.ValidationError("Please correct the errors below.")

        if active_time > start_time:
            raise forms.ValidationError("Active time must be before start time.")
        if end_time < start_time:
            raise forms.ValidationError("Start time must be before end time.")
        if frozen_time and frozen_time > end_time:
            raise forms.ValidationError("Frozen time must be before end time.")
        if unfrozen_time and unfrozen_time < end_time:
            raise forms.ValidationError("Unfrozen time must be after end time.")
        if deactivate_time and deactivate_time < end_time:
            raise forms.ValidationError("Deactivate time must be after end time.")
        return cleaned_data