
from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404, JsonResponse, FileResponse
from django.core.files import File
from django.contrib import messages
from django.db import IntegrityError
from .forms import UserRegister, AdminRegister, Login, SubmitAnswer, ForgotPassword, EditUserProfile, ChangePassword, \
    EditAdminProfile, AddProblem, AddUser, EditProblem, AddSample, ContestRegister, EditContest
from .models import User, Admin, Campus, Problem, Submit, SubmitOutput, TestCase, Contest
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.safestring import mark_safe
from django.contrib import messages
from datetime import datetime, timedelta
import pytz, os, time, subprocess, dateutil.parser


def homepage(request):
    return render_to_response('webpages/homepage.html')


def user_register(request):

    if request.method == "POST":
        form = UserRegister(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            date = datetime.now().date()
            password = request.POST.get('user_password')
            if request.FILES.get('photo'):
                post.photo = request.FILES.get('photo')
            post.register_date = date
            post.password = password
            # post.is_active = 'nonactive'
            # email_confirmation(request, post.email, post)
            post.save()
            messages.success(request, "signup successfully.")

            # messages.success(request, "Please confirm your email address to complete the registration.")
    else:
        form = UserRegister()
    return render(request, 'webpages/user_register.html', {'form': form})


def admin_register(request):

    if request.method == "POST":
        form = AdminRegister(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            date = datetime.now().date()
            password = request.POST.get('user_password')
            if request.FILES.get('photo'):
                post.photo = request.FILES.get('photo')
            post.register_date = date
            post.password = password
            # post.is_active = 'nonactive'
            # email_confirmation(request, post.email, post)
            post.save()
            messages.success(request, "signup successfully.")

            # messages.success(request, "Please confirm your email address to complete the registration.")
    else:
        form = AdminRegister()
    return render(request, 'webpages/admin_register.html', {'form': form})


def contest_filter(request, email):
    user = User.objects.get(email=email)
    utc = pytz.UTC
    date = utc.localize(datetime.now())
    contest_id = request.session.get('contest')
    contest = Contest.objects.filter(user=user, active_time__lt=date, deactivate_time__gt=date,
                                     enable='yes').order_by('start_time')
    if len(contest) == 1:
        contest = []
    for i in contest:
        if contest_id == str(i.id):
            i.selected = 'yes'
        else:
            i.selected = 'no'
    return contest


def admin_view_contest_form(request, email):
    admin = Admin.objects.get(email=email)
    utc = pytz.UTC
    date = utc.localize(datetime.now())
    contest_id = request.session.get('admin_contest')
    contest = Contest.objects.filter(campus=admin.campus, active_time__lt=date, deactivate_time__gt=date,
                                     enable='yes').order_by('start_time')
    for i in contest:
        if contest_id == str(i.id):
            i.selected = 'yes'
        else:
            i.selected = 'no'
    return contest



def add_user(request):
    admin_email = request.session.get('admin_auth')
    if not admin_email:
        raise Http404('You are not logged in')
    contest = admin_view_contest_form(request, admin_email)
    if request.method == "POST":
        form = AddUser(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            password = get_random_string(6, chars)
            utc = pytz.UTC
            date = utc.localize(datetime.now())

            if request.FILES.get('photo'):
                post.photo = request.FILES.get('photo')
            post.register_date = date
            post.password = password
            post.campus = Admin.objects.get(email=admin_email).campus
            # post.is_active = 'nonactive'
            # email_confirmation(request, post.email, post)
            post.save()
            messages.success(request, "the user was added successfully.")

            # messages.success(request, "Please confirm your email address to complete the registration.")
    else:
        form = AddUser()
    return render(request, 'webpages/add_user.html', {'form': form, 'contest': contest})


def login(request):
    if request.method == "POST":
        form = Login(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            utc = pytz.UTC
            date = utc.localize(datetime.now())
            try:
                User.objects.get(email=email)
                request.session['user_auth'] = email
                user = User.objects.get(email=email)
                contest = Contest.objects.filter(user=user, active_time__lt=date,
                                                 deactivate_time__gt=date,
                                                 enable='yes').order_by('start_time')
                if contest:
                    request.session['contest'] = contest[0].id
                else:
                    request.session['contest'] = None
                return redirect('/user-homepage/')
            except User.DoesNotExist:
                try:
                    Admin.objects.get(email=email)
                    admin = Admin.objects.get(email=email)
                    request.session['admin_auth'] = email

                    contest = Contest.objects.filter(campus=admin.campus, active_time__lt=date,
                                                     deactivate_time__gt=date,
                                                     enable='yes').order_by('start_time')
                    if contest:
                        request.session['admin_contest'] = contest[0].id
                    else:
                        request.session['admin_contest'] = None

                    return redirect('/admin-homepage/')
                except Admin.DoesNotExist:
                    raise Http404("e-mail does not exist")

    else:
        form = Login()
    return render(request, 'webpages/login.html', {'form': form})


def admin_homepage(request):
    admin_email = request.session.get('admin_auth')
    if not admin_email:
        raise Http404("You are not Logged in")
    contest = admin_view_contest_form(request, admin_email)

    return render(request, 'webpages/admin_homepage.html', {'contest': contest})


def user_homepage(request):
    user_email = request.session.get('user_auth')
    if not user_email:
        raise Http404("You are not Logged in")

    contest = contest_filter(request, user_email)
    return render(request, 'webpages/user_homepage.html', {'contest': contest})


def logout(request, role):
    if role == 'user':
        request.session['user_auth'] = None
        request.session['contest'] = None
    elif role == 'admin':
        request.session['admin_auth'] = None
        request.session['admin_contest'] = None
    else:
        pass
    return redirect('/homepage/')


def forgot_password(request):
    if request.method == "POST":
        form = ForgotPassword(request.POST)
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        secret_key = get_random_string(8, chars)

        if form.is_valid():
            email = request.POST.get('email')
            recipient_list = [email]
            message = secret_key
            subject = 'This mail is from ASTUEvent Organizer.'
            email_from = settings.EMAIL_HOST_USER

            try:
                user = User.objects.get(email=email)

                send_mail(subject, message, email_from, recipient_list, fail_silently=False)
                user.password = secret_key
                user.save()
            except User.DoesNotExist:
                try:
                    admin = Admin.objects.get(email=email)
                    send_mail(subject, message, email_from, recipient_list, fail_silently=False)
                    admin.password = secret_key
                    admin.save()
                except Admin.DoesNotExist:
                    raise Http404("Your E-mail is invalid please insert valid E-mail")
            return redirect('/login/')

    else:
        form = ForgotPassword()
    return render(request, 'webpages/forget_password.html', {'form': form})



def view_user_profile(request):
    user_email = request.session.get('user_auth')
    if not user_email:
        raise Http404("You are not Logged in")

    contest = contest_filter(request, user_email)
    if request.method == "POST":
        form = EditUserProfile(request.POST, request.FILES, user_email=user_email)
        if form.is_valid():

            user.name = request.POST.get('name')
            user.middle_name = request.POST.get('middle_name')
            user.last_name = request.POST.get('last_name')
            user.phone = request.POST.get('phone')
            user.email = request.POST.get('email')
            user.sex = request.POST.get('sex')
            user.campus = Campus.objects.get(pk=request.POST.get('campus'))
            if request.FILES.get('photo'):
                user.photo = request.FILES.get('photo')
            user.save()
            if request.session['user_auth'] != request.POST.get('email'):
                # user.is_active = False
                # user.save()
                # email_confirmation(request, request.POST.get('email'), user)
                request.session['user_auth'] = request.POST.get('email')

            messages.success(request, "The user "+user.name+" was update successfully.")
            return redirect('/user-profile/')

    else:
        form = EditUserProfile(user_email=user_email)
    return render(request, 'webpages/user_profile.html', {'form': form, 'contest': contest})


def view_admin_profile(request):
    admin_email = request.session.get('admin_auth')
    if not admin_email:
        raise Http404("You are not Logged in")
    contest = admin_view_contest_form(request, admin_email)
    if request.method == "POST":
        form = EditAdminProfile(request.POST, request.FILES, admin_email=admin_email)
        if form.is_valid():
            admin = Admin.objects.get(email=admin_email)
            admin.name = request.POST.get('name')
            admin.middle_name = request.POST.get('middle_name')
            admin.last_name = request.POST.get('last_name')
            admin.phone = request.POST.get('phone')
            admin.email = request.POST.get('email')
            admin.sex = request.POST.get('sex')
            admin.campus = Campus.objects.get(pk=request.POST.get('campus'))
            if request.FILES.get('photo'):
                admin.photo = request.FILES.get('photo')
            admin.save()
            if request.session['admin_auth'] != request.POST.get('email'):
                # admin.is_active = False
                # admin.save()
                # email_confirmation(request, request.POST.get('email'), user)
                request.session['admin_auth'] = request.POST.get('email')

            messages.success(request, "The admin "+admin.name+" was update successfully.")
            return redirect('/admin-profile/')

    else:
        form = EditAdminProfile(admin_email=admin_email)
    return render(request, 'webpages/admin_profile.html', {'form': form, 'contest': contest})


def change_password(request, role):
    if role == 'user':
        user_email = request.session.get('user_auth')
        if user_email:
            contest = contest_filter(request, user_email)

            if request.method == "POST":
                form = ChangePassword(request.POST, key=user.password)
                if form.is_valid():
                    user.password = request.POST.get('new_password')
                    user.save()
                    messages.success(request, "The password was changed successfully.")
                    return HttpResponseRedirect('/user-profile/')

            else:
                form = ChangePassword(key=user.password)
        else:
            raise Http404("You are not logged in")

    elif role == 'admin':
        admin_email = request.session.get('admin_auth')
        if admin_email:
            admin = Admin.objects.get(email=admin_email)
            contest = admin_view_contest_form(request, admin_email)
            if request.method == "POST":
                form = ChangePassword(request.POST, key=admin.password)
                if form.is_valid():
                    admin.password = request.POST.get('new_password')
                    admin.save()
                    messages.success(request, "The password was changed successfully.")
                    return HttpResponseRedirect('/admin-profile/')
            else:
                form = ChangePassword(key=admin.password)
        else:
            raise Http404("You are not logged in")

    else:
        raise Http404("You are not logged in")

    return render(request, 'webpages/change_password.html', {'form': form, 'role': role, 'contest': contest})


def submit_answer(request):
    email = request.session.get('user_auth')
    if not email:
        raise Http404("You are not Logged in")
    contest_id = request.session.get('contest')
    user = User.objects.get(email=email)
    contest = contest_filter(request, email)

    try:
        current_contest = Contest.objects.get(pk=contest_id)
    except Contest.DoesNotExist:
        current_contest = None

    overview = Submit.objects.filter(contest=current_contest, user=user).order_by('submit_time').reverse()
    for i in overview:
        if i.submit_time > current_contest.end_time:
            i.result = 'Too Late'
    # print(overview, contest_id, current_contest)
    if request.method == "POST":
        form = SubmitAnswer(request.POST, request.FILES, current_contest_id=contest_id)
        if form.is_valid():
            user = User.objects.get(email=email)

            file = request.FILES.get('file')
            language = request.POST.get('language')
            problem_id = request.POST.get('problem')
            try:
                problem_obj = Problem.objects.get(pk=problem_id)
            except Problem.DoesNotExist:
                raise Http404("Problem is not registered")

            submit = Submit(submit_answer=file, user=user, problem=problem_obj, submit_time=date, language=language,
                            contest=current_contest)
            submit.save()
            test_cases = [i for i in TestCase.objects.filter(problem=problem_obj)]
            time_limit = problem_obj.time_limit
            memory_limit = float('inf')
            if problem_obj.memory_limit:
                memory_limit = problem_obj.memory_limit
            file_name = 'judge/static/Images/' + submit.submit_answer.name

            # exe_file_2 = "judge\static\Images\\file\\"+submit.submit_answer.name[5:-4]+".exe"
            # print(exe_file_1, exe_file_2)
            # print(file_name,os.getcwd())
            if language == 'C++':
                # os.system("g++ " + file_name + " -o judge/static/Images/file/tester.exe")
                exe_file_1 = "judge/static/Images/" + \
                             (submit.submit_answer.name[::-1].replace('cpp'[::-1], 'exe'[::-1], 1)[::-1])
                exe_file_2 = exe_file_1.replace("/", "\\")
                if os.path.exists(file_name):
                    failure = os.system("g++ " + file_name + " -o "+exe_file_1)
                    if failure:
                        submit.result = "Compiler Error"
                        submit.save()
                        # messages.error(request, "Compiler Error")
                    else:
                        all_correct = True
                        for each in test_cases:
                            input_file = each.input
                            # print(input_file)
                            try:
                                user_output = File(open('_user_output.txt', 'r'))
                                insert = SubmitOutput(output=user_output, user=user, test_case=each, submit=submit)
                                insert.save()
                            except IntegrityError:
                                pass

                            initial_time = time.clock()
                            failure = os.system(exe_file_2 + "<judge\static\Images\\" + input_file.name +
                                                ">judge\static\Images\\" + insert.output.name)
                            final_time = time.clock()
                            # print(final_time - initial_time, time_limit)
                            if failure:
                                insert.result = "Run Time Error"
                                insert.save()
                                submit.result = "Run Time Error"
                                submit.save()
                                # messages.error(request, "Run Time Error")
                                all_correct = 0
                                break

                            elif final_time - initial_time > time_limit:
                                insert.result = 'Time Limit Exceeded'
                                insert.save()
                                submit.result = "Time Limit Exceeded"
                                submit.save()
                                # messages.error(request, "Time Limit Exceeded")
                                all_correct = 0
                                break
                            else:
                                correct_answer_file = "judge/static/Images/" + each.output.name
                                correct_answer = open(correct_answer_file, 'r')
                                user_answer_file = "judge/static/Images/" + insert.output.name
                                user_answer = open(user_answer_file, 'r')
                                correct_answer_list = []
                                user_answer_list = []

                                for j in correct_answer:
                                    correct_answer_list.append(j)
                                for j in user_answer:
                                    user_answer_list.append(j)

                                correct_answer.close()
                                user_answer.close()

                                # user_code_memory = submit.submit_answer.size
                                if insert.output.size/1000000.0 > memory_limit:
                                    submit.result = "Memory Limit Exceeded"
                                    submit.save()
                                    # messages.error(request, "Memory Limit Exceeded")
                                elif correct_answer_list and not user_answer_list:
                                    insert.result = 'No Output'
                                    insert.save()
                                    submit.result = "No Output"
                                    submit.save()
                                    # messages.error(request, "No Output")
                                    all_correct = 0
                                    break
                                elif correct_answer_list == user_answer_list:
                                    insert.result = 'Correct'
                                    insert.save()
                                else:
                                    insert.result = 'Wrong Answer'
                                    insert.save()
                                    submit.result = "Wrong Answer"
                                    submit.save()
                                    # messages.error(request, "Wrong Answer")
                                    all_correct = 0
                                    break
                        if all_correct:
                            submit.result = "Correct"
                            submit.save()
                            # messages.success(request, "Correct")

                else:
                    raise Http404("file does not exist.")
            elif language == 'C':
                exe_file_1 = "judge/static/Images/" + \
                             (submit.submit_answer.name[::-1].replace('c'[::-1], 'exe'[::-1], 1)[::-1])
                exe_file_2 = exe_file_1.replace("/", "\\")
                if os.path.exists(file_name):
                    failure = os.system("g++ " + file_name + " -o " + exe_file_1)
                    if failure:
                        submit.result = "Compiler Error"
                        submit.save()
                        # messages.error(request, "Compiler Error")
                    else:
                        all_correct = True
                        for each in test_cases:
                            input_file = each.input
                            # print(input_file)
                            try:
                                user_output = File(open('_user_output.txt', 'r'))
                                insert = SubmitOutput(output=user_output, user=user, test_case=each, submit=submit)
                                insert.save()
                            except IntegrityError:
                                pass

                            initial_time = time.clock()
                            failure = os.system(exe_file_2 + "<judge\static\Images\\" + input_file.name +
                                                ">judge\static\Images\\" + insert.output.name)
                            final_time = time.clock()
                            # print(final_time - initial_time, time_limit)
                            if failure:
                                insert.result = "Run Time Error"
                                insert.save()
                                submit.result = "Run Time Error"
                                submit.save()
                                # messages.error(request, "Run Time Error")
                                all_correct = 0
                                break

                            elif final_time - initial_time > time_limit:
                                insert.result = 'Time Limit Exceeded'
                                insert.save()
                                submit.result = "Time Limit Exceeded"
                                submit.save()
                                # messages.error(request, "Time Limit Exceeded")
                                all_correct = 0
                                break
                            else:
                                correct_answer_file = "judge/static/Images/" + each.output.name
                                correct_answer = open(correct_answer_file, 'r')
                                user_answer_file = "judge/static/Images/" + insert.output.name
                                user_answer = open(user_answer_file, 'r')
                                correct_answer_list = []
                                user_answer_list = []

                                for j in correct_answer:
                                    correct_answer_list.append(j)
                                for j in user_answer:
                                    user_answer_list.append(j)

                                correct_answer.close()
                                user_answer.close()

                                # user_code_memory = submit.submit_answer.size
                                if insert.output.size / 1000000.0 > memory_limit:
                                    submit.result = "Memory Limit Exceeded"
                                    submit.save()
                                    # messages.error(request, "Memory Limit Exceeded")
                                elif correct_answer_list and not user_answer_list:
                                    insert.result = 'No Output'
                                    insert.save()
                                    submit.result = "No Output"
                                    submit.save()
                                    # messages.error(request, "No Output")
                                    all_correct = 0
                                    break
                                elif correct_answer_list == user_answer_list:
                                    insert.result = 'Correct'
                                    insert.save()
                                else:
                                    insert.result = 'Wrong Answer'
                                    insert.save()
                                    submit.result = "Wrong Answer"
                                    submit.save()
                                    # messages.error(request, "Wrong Answer")
                                    all_correct = 0
                                    break
                        if all_correct:
                            submit.result = "Correct"
                            submit.save()
                            # messages.success(request, "Correct")

                else:
                    raise Http404("file does not exist.")

            elif language == 'Java':
                # os.system("g++ " + file_name + " -o judge/static/Images/file/tester.exe")
                exe_file_1 = submit.submit_answer.name[:-5]
                exe_file_2 = (exe_file_1[::-1].replace('/', ' ', 1))[::-1]
                exe_file_2 = exe_file_2.replace('/', '\\')
                exe_file_2 = "judge\static\Images\\"+exe_file_2
                file_name = file_name.replace("/", "\\")
                # print(exe_file_1, exe_file_2, file_name)
                if os.path.exists(file_name):
                    failure = os.system("javac " + file_name)
                    if failure:
                        submit.result = "Compiler Error"
                        submit.save()
                        # messages.error(request, "Compiler Error")
                    else:
                        all_correct = True
                        for each in test_cases:
                            input_file = each.input

                            try:
                                user_output = File(open('_user_output.txt', 'r'))
                                insert = SubmitOutput(output=user_output, user=user, test_case=each, submit=submit)
                                insert.save()
                            except IntegrityError:
                                pass

                            initial_time = time.clock()
                            failure = os.system("java -cp "+exe_file_2 + "<judge\static\Images\\" + input_file.name +
                                                ">judge\static\Images\\" + insert.output.name)
                            final_time = time.clock()
                            # print(final_time - initial_time, time_limit)
                            if failure:
                                insert.result = "Run Time Error"
                                insert.save()
                                submit.result = "Run Time Error"
                                submit.save()
                                messages.error(request, "Run Time Error")
                                all_correct = 0
                                break

                            elif final_time - initial_time > time_limit:
                                insert.result = 'Time Limit Exceeded'
                                insert.save()
                                submit.result = "Time Limit Exceeded"
                                submit.save()
                                # messages.error(request, "Time Limit Exceeded")
                                all_correct = 0
                                break
                            else:
                                correct_answer_file = "judge/static/Images/" + each.output.name
                                correct_answer = open(correct_answer_file, 'r')
                                user_answer_file = "judge/static/Images/" + insert.output.name
                                user_answer = open(user_answer_file, 'r')
                                correct_answer_list = []
                                user_answer_list = []

                                for j in correct_answer:
                                    correct_answer_list.append(j)
                                for j in user_answer:
                                    user_answer_list.append(j)

                                correct_answer.close()
                                user_answer.close()

                                # user_code_memory = submit.submit_answer.size
                                if insert.output.size/1000000.0 > memory_limit:
                                    submit.result = "Memory Limit Exceeded"
                                    submit.save()
                                    # messages.error(request, "Memory Limit Exceeded")
                                elif correct_answer_list and not user_answer_list:
                                    insert.result = 'No Output'
                                    insert.save()
                                    submit.result = "No Output"
                                    submit.save()
                                    # messages.error(request, "No Output")
                                    all_correct = 0
                                    break
                                elif correct_answer_list == user_answer_list:
                                    insert.result = 'Correct'
                                    insert.save()
                                else:
                                    insert.result = 'Wrong Answer'
                                    insert.save()
                                    submit.result = "Wrong Answer"
                                    submit.save()
                                    # messages.error(request, "Wrong Answer")
                                    all_correct = 0
                                    break
                        if all_correct:
                            submit.result = "Correct"
                            submit.save()
                            # messages.success(request, "Correct")

                else:
                    raise Http404("file does not exist.")

            elif language == 'Python2':
                exe_file = file_name
                if os.path.exists(file_name):

                    failure = os.system("python2 -m py_compile " + file_name)
                    if failure:
                        submit.result = "Compiler Error"
                        submit.save()
                        # messages.error(request, "Compiler Error")
                    else:

                        all_correct = True
                        for each in test_cases:
                            input_file = each.input
                            try:
                                user_output = File(open('_user_output.txt', 'r'))
                                insert = SubmitOutput(output=user_output, user=user, test_case=each, submit=submit)
                                insert.save()
                            except IntegrityError:
                                pass

                            initial_time = time.clock()
                            failure = os.system("python2 " + exe_file + "<judge\static\Images\\" + input_file.name +
                                                ">judge\static\Images\\" + insert.output.name)

                            final_time = time.clock()
                            if failure:
                                insert.result = "Run Time Error"
                                insert.save()
                                submit.result = "Run Time Error"
                                submit.save()
                                # messages.error(request, "Run Time Error")
                                all_correct = 0
                                break

                            elif final_time - initial_time > time_limit:
                                insert.result = 'Time Limit Exceeded'
                                insert.save()
                                submit.result = "Time Limit Exceeded"
                                submit.save()
                                # messages.error(request, "Time Limit Exceeded")
                                all_correct = 0
                                break
                            else:
                                correct_answer_file = "judge/static/Images/" + each.output.name
                                correct_answer = open(correct_answer_file, 'r')
                                user_answer_file = "judge/static/Images/" + insert.output.name
                                user_answer = open(user_answer_file, 'r')
                                correct_answer_list = []
                                user_answer_list = []

                                for j in correct_answer:
                                    correct_answer_list.append(j)
                                for j in user_answer:
                                    user_answer_list.append(j)

                                correct_answer.close()
                                user_answer.close()

                                # user_code_memory = submit.submit_answer.size
                                if insert.output.size / 1000000.0 > memory_limit:
                                    submit.result = "Memory Limit Exceeded"
                                    submit.save()
                                    # messages.error(request, "Memory Limit Exceeded")
                                elif correct_answer_list and not user_answer_list:
                                    insert.result = 'No Output'
                                    insert.save()
                                    submit.result = "No Output"
                                    submit.save()
                                    # messages.error(request, "No Output")
                                    all_correct = 0
                                    break
                                elif correct_answer_list == user_answer_list:
                                    insert.result = 'Correct'
                                    insert.save()
                                else:
                                    insert.result = 'Wrong Answer'
                                    insert.save()
                                    submit.result = "Wrong Answer"
                                    submit.save()
                                    # messages.error(request, "Wrong Answer")
                                    all_correct = 0
                                    break
                        if all_correct:
                            submit.result = "Correct"
                            submit.save()
                            # messages.success(request, "Correct")

                else:
                    raise Http404("file does not exist.")
            elif language == 'Python3':
                exe_file = file_name
                if os.path.exists(file_name):
                    failure = os.system("python -m py_compile " + file_name)
                    if failure:
                        submit.result = "Compiler Error"
                        submit.save()
                        # messages.error(request, "Compiler Error")
                    else:

                        all_correct = True
                        for each in test_cases:
                            input_file = each.input
                            try:
                                user_output = File(open('_user_output.txt', 'r'))
                                insert = SubmitOutput(output=user_output, user=user, test_case=each, submit=submit)
                                insert.save()
                            except IntegrityError:
                                pass

                            initial_time = time.clock()

                            failure = os.system("python " + exe_file + "<judge\static\Images\\" + input_file.name +
                                                ">judge\static\Images\\" + insert.output.name)

                            final_time = time.clock()
                            if failure:
                                insert.result = "Run Time Error"
                                insert.save()
                                submit.result = "Run Time Error"
                                submit.save()
                                # messages.error(request, "Run Time Error")
                                all_correct = 0
                                break

                            elif final_time - initial_time > time_limit:
                                insert.result = 'Time Limit Exceeded'
                                insert.save()
                                submit.result = "Time Limit Exceeded"
                                submit.save()
                                # messages.error(request, "Time Limit Exceeded")
                                all_correct = 0
                                break
                            else:
                                correct_answer_file = "judge/static/Images/" + each.output.name
                                correct_answer = open(correct_answer_file, 'r')
                                user_answer_file = "judge/static/Images/" + insert.output.name
                                user_answer = open(user_answer_file, 'r')
                                correct_answer_list = []
                                user_answer_list = []

                                for j in correct_answer:
                                    correct_answer_list.append(j)
                                for j in user_answer:
                                    user_answer_list.append(j)

                                correct_answer.close()
                                user_answer.close()

                                # user_code_memory = submit.submit_answer.size
                                if insert.output.size / 1000000.0 > memory_limit:
                                    submit.result = "Memory Limit Exceeded"
                                    submit.save()
                                    # messages.error(request, "Memory Limit Exceeded")
                                elif correct_answer_list and not user_answer_list:
                                    insert.result = 'No Output'
                                    insert.save()
                                    submit.result = "No Output"
                                    submit.save()
                                    # messages.error(request, "No Output")
                                    all_correct = 0
                                    break
                                elif correct_answer_list == user_answer_list:
                                    insert.result = 'Correct'
                                    insert.save()
                                else:
                                    insert.result = 'Wrong Answer'
                                    insert.save()
                                    submit.result = "Wrong Answer"
                                    submit.save()
                                    # messages.error(request, "Wrong Answer")
                                    all_correct = 0
                                    break
                        if all_correct:
                            submit.result = "Correct"
                            submit.save()
                            # messages.success(request, "Correct")

                else:
                    raise Http404("file does not exist.")
        return redirect('/overview/')

    else:
        form = SubmitAnswer(current_contest_id=contest_id)

    return render(request, 'webpages/submit_answer.html', {'form': form, 'contest': contest, 'overview': overview})


def add_problem(request):
    admin_email = request.session.get('admin_auth')
    if not admin_email:
        raise Http404('You are not logged in')

    contest = admin_view_contest_form(request, admin_email)
    if request.method == "POST":
        form = AddProblem(request.POST, request.FILES)
        if form.is_valid():
            admin = Admin.objects.get(email=admin_email)
            post = form.save(commit=False)
            utc = pytz.UTC
            date = utc.localize(datetime.now())

            post.register_date = date
            post.campus = admin.campus

            post.save()
            '''
            insert = TestCase(problem=post, input=request.FILES.get('sample_input'),
                              output=request.FILES.get('sample_output'), name='t1')
            insert.save()
            '''

            messages.success(request, "problem "+post.title+" was added successfully.")
            return redirect('/view-problem-by-admin/')
    else:
        form = AddProblem()
    return render(request, 'webpages/add_problem.html', {'form': form, 'contest': contest})


def view_problem_by_admin(request):
    admin_email = request.session.get('admin_auth')
    contest = admin_view_contest_form(request, admin_email)
    if admin_email:
        admin = Admin.objects.get(email=admin_email)

        problem = Problem.objects.filter(campus=admin.campus)

        problem = sorted(problem, key=lambda x: x.register_date, reverse=True)
        for i in problem:
            i.link = '/media/'+str(i.pdf)
        return render(request, 'webpages/problem_view_by_admin.html', {'problem': problem, 'contest': contest})

    else:
        raise Http404("You are not logged in")


def user_view_by_admin(request):
    admin_email = request.session.get('admin_auth')
    contest = admin_view_contest_form(request, admin_email)
    if admin_email:
        admin = Admin.objects.get(email=admin_email)

        user = User.objects.filter(campus=admin.campus)

        user = sorted(user, key=lambda x: x.name, reverse=False)

        for i in user:
            i.image = "Images/" + str(i.photo)
        return render(request, 'webpages/user_view_by_admin.html', {'user': user, 'contest': contest})

    else:
        raise Http404("You are not logged in")


def not_delete(request, page):

    if page == 'user_delete':
        return redirect('/admin-view-user/')
    elif page == 'problem':
        return redirect('/view-problem-by-admin/')
    elif page == 'contest':
        return redirect('/view-contest-by-admin/')


def delete_user_confirm(request, user_id):
    if request.session.get('admin_auth'):
        user = User.objects.get(pk=user_id)
        contest = admin_view_contest_form(request, request.session.get('admin_auth'))
        return render(request, 'webpages/delete_user_confirmation.html', {'user': user, 'contest': contest})

    else:
        raise Http404("You are not logged in")


def delete_user(request, user_id):
    if request.session.get('admin_auth'):
        contest = admin_view_contest_form(request, request.session.get('admin_auth'))
        try:
            user = User.objects.get(pk=user_id)
            user.delete()
            messages.success(request, "The user " + user.name + " was deleted successfully.")
            return redirect('/admin-view-user/')
        except User.DoesNotExist:
            raise Http404("This user is not registered")
    else:
        raise Http404("You are not logged in")


def delete_problem_confirm(request, problem_id):
    if request.session.get('admin_auth'):
        contest = admin_view_contest_form(request, request.session.get('admin_auth'))
        problem = Problem.objects.get(pk=problem_id)

        return render(request, 'webpages/delete_problem_confirmation.html', {'problem': problem, 'contest': contest})

    else:
        raise Http404("You are not logged in")


def delete_problem(request, problem_id):
    if request.session.get('admin_auth'):
        try:
            problem = Problem.objects.get(pk=problem_id)
            problem.delete()
            messages.success(request, "The problem " + problem.title + " was deleted successfully.")
            return redirect('/view-problem-by-admin/')
        except Problem.DoesNotExist:
            raise Http404("The problem was not registered")
    else:
        raise Http404("You are not logged in")


def edit_problem(request, problem_id):
    admin_email = request.session.get('admin_auth')
    if not admin_email:
        raise Http404("You are not Logged in")
    contest = admin_view_contest_form(request, admin_email)
    if request.method == "POST":
        form = EditProblem(request.POST, request.FILES, problem_id=problem_id)
        if form.is_valid():
            problem = Problem.objects.get(pk=problem_id)
            problem.title = request.POST.get('title')
            problem.time_limit = request.POST.get('time_limit')
            if request.POST.get('memory_limit'):
                problem.memory_limit = request.POST.get('memory_limit')
            else:
                problem.memory_limit = None
            problem.point = request.POST.get('point')

            if request.FILES.get('pdf'):
                problem.pdf = request.FILES.get('pdf')
            problem.save()

            messages.success(request, "The problem "+problem.title+" was update successfully.")

    else:
        form = EditProblem(problem_id=problem_id)
    return render(request, 'webpages/edit_problem.html', {'form': form, 'problem_id': problem_id, 'contest': contest})


def add_sample(request, problem_id):
    admin_email = request.session.get('admin_auth')
    if not admin_email:
        raise Http404("You are not Logged in")
    contest = admin_view_contest_form(request, admin_email)
    problem = Problem.objects.get(pk=problem_id)
    last = TestCase.objects.filter(problem=problem).order_by('name')
    test_case = [i for i in last]
    for i in test_case:
        i.input_link = '/media/' + str(i.input)
        i.output_link = '/media/' + str(i.output)
    if request.method == "POST":

        for i in test_case:
            if request.FILES.get(i.input_link):
                i.input = request.FILES.get(i.input_link)
            if request.FILES.get(i.output_link):
                i.output = request.FILES.get(i.output_link)
            i.save()

        form = AddSample(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)

            name = 't'+str(len(last)+1)
            post.problem = problem
            post.name = name
            post.save()
            messages.success(request, "The sample "+post.name+" was added successfully.")
        url = request.META['HTTP_REFERER']
        return redirect(url)
    else:
        form = AddSample()
    return render(request, 'webpages/add_sample.html', {'form': form, 'test_case': test_case, 'contest': contest})


def delete_test_case_confirm(request, test_case_id):
    if request.session.get('admin_auth'):
        contest = admin_view_contest_form(request, request.session.get('admin_auth'))
        test_case = TestCase.objects.get(pk=test_case_id)

        return render(request, 'webpages/delete_test_case_confirmation.html', {'test_case': test_case, 'contest': contest})

    else:
        raise Http404("You are not logged in")


def delete_test_case(request, test_case_id):
    if request.session.get('admin_auth'):
        contest = admin_view_contest_form(request, request.session.get('admin_auth'))
        try:
            test_case = TestCase.objects.get(pk=test_case_id)
            test_case.delete()
            messages.success(request, "Test case " + test_case.name + " was deleted successfully.")
            return redirect('/view-problem-by-admin/')
        except TestCase.DoesNotExist:
            raise Http404("The test case was not registered")
    else:
        raise Http404("You are not logged in")


def view_submission(request):
    admin_email = request.session.get('admin_auth')
    if admin_email:
        contest = admin_view_contest_form(request, request.session.get('admin_auth'))
        try:
            admin = Admin.objects.get(email=admin_email)
            submit = Submit.objects.filter(user__campus=admin.campus).order_by('submit_time').reverse()
            return render(request, 'webpages/submission_view.html', {'submit': submit, 'contest': contest})

        except Admin.DoesNotExist:
            raise Http404("The admin was not registered")
    else:
        raise Http404("You are not logged in")


def view_problem_by_user(request):
    email = request.session.get('user_auth')
    if email:
        utc = pytz.UTC
        date = utc.localize(datetime.now())
        contest_id = request.session.get('contest')
        user = User.objects.get(email=email)
        try:
            current_contest = Contest.objects.get(pk=contest_id)
            problem = current_contest.problem.all()
        except Contest.DoesNotExist:
            raise Http404("The contest is not registered.")

        problem = sorted(problem, key=lambda x: x.title.lower())
        for i in problem:
            i.link = '/media/'+str(i.pdf)

        contest = Contest.objects.filter(user=user, active_time__lt=date, deactivate_time__gt=date,
                                         enable='yes').order_by('start_time')
        contest = contest_filter(request, email)
        return render(request, 'webpages/problem_view_by_user.html', {'problem': problem, 'contest': contest})

    else:
        raise Http404("You are not logged in")


def add_contest(request):
    admin_email = request.session.get('admin_auth')
    if not admin_email:
        raise Http404('You are not logged in')
    admin = Admin.objects.get(email=admin_email)
    contest = admin_view_contest_form(request, request.session.get('admin_auth'))
    if request.method == "POST":
        form = ContestRegister(request.POST, request.FILES, campus=admin.campus)
        if form.is_valid():
            post = form.save(commit=False)

            utc = pytz.UTC
            date = utc.localize(datetime.now())

            post.register_date = date
            post.campus = admin.campus
            post.save()
            form.save_m2m()
            messages.success(request, "The contest "+post.title+" was added successfully.")
    else:
        form = ContestRegister(campus=admin.campus)
    return render(request, 'webpages/add_contest.html', {'form': form, 'contest': contest})


def view_contest_by_admin(request):
    admin_email = request.session.get('admin_auth')
    contest = admin_view_contest_form(request, request.session.get('admin_auth'))
    if admin_email:
        try:
            admin = Admin.objects.get(email=admin_email)
            total_contest = Contest.objects.filter(campus=admin.campus).order_by('start_time').reverse()
            return render(request, 'webpages/contest_view_by_admin.html',
                          {'total_contest': total_contest, 'contest': contest})

        except Admin.DoesNotExist:
            raise Http404("The admin was not registered")
    else:
        raise Http404("You are not logged in")


def delete_contest_confirm(request, contest_id):
    if request.session.get('admin_auth'):
        contest = admin_view_contest_form(request, request.session.get('admin_auth'))
        delete_contest = Contest.objects.get(pk=contest_id)

        return render(request, 'webpages/delete_contest_confirmation.html', {'delete_contest': delete_contest, 'contest': contest})

    else:
        raise Http404("You are not logged in")


def delete_contest(request, contest_id):
    if request.session.get('admin_auth'):
        try:
            contest = Contest.objects.get(pk=contest_id)
            contest.delete()
            messages.success(request, "The contest " + contest.title + " was deleted successfully.")
            return redirect('/view-contest-by-admin/')
        except Contest.DoesNotExist:
            raise Http404("The contest was not registered")
    else:
        raise Http404("You are not logged in")


def edit_contest(request, contest_id):
    admin_email = request.session.get('admin_auth')
    if not admin_email:
        raise Http404("You are not Logged in")
    contest = admin_view_contest_form(request, request.session.get('admin_auth'))
    current_contest = Contest.objects.get(pk=contest_id)
    if request.method == "POST":
        form = EditContest(request.POST, request.FILES, contest_id=contest_id,
                           initial={'user': current_contest.user.all(), 'problem': current_contest.problem.all(),
                                    'title': current_contest.title})
        if form.is_valid():
            utc = pytz.UTC

            current_contest.title = request.POST.get('title')
            current_contest.active_time = utc.localize(dateutil.parser.parse(request.POST.get('active_time')))
            current_contest.start_time = utc.localize(dateutil.parser.parse(request.POST.get('start_time')))
            current_contest.end_time = utc.localize(dateutil.parser.parse(request.POST.get('end_time')))
            current_contest.frozen_time = utc.localize(dateutil.parser.parse(request.POST.get('frozen_time')))
            current_contest.unfrozen_time = utc.localize(dateutil.parser.parse(request.POST.get('unfrozen_time')))
            current_contest.deactivate_time = utc.localize(dateutil.parser.parse(request.POST.get('deactivate_time')))
            if request.FILES.get('photo'):
                current_contest.pdf = request.FILES.get('photo')

            pro = request.POST.getlist('problem')
            problem_list = set()

            for i in pro:
                try:
                    problem = Problem.objects.get(pk=i)
                except Problem.DoesNotExist:
                    raise Http404("The problem with pk " + i + " was not registered")
                problem_list.add(problem)
            current_contest.problem.set(problem_list)
            current_contest.save()

            user = request.POST.getlist('user')
            user_list = set()
            for i in user:
                try:
                    new_user = User.objects.get(pk=i)
                except User.DoesNotExist:
                    raise Http404("The user with pk " + i + " was not registered")
                user_list.add(new_user)

            current_contest.user.set(user_list)
            current_contest.save()

            # contest.save_m2m()
            messages.success(request, "The contest "+current_contest.title+" was update successfully.")

    else:
        form = EditContest(contest_id=contest_id,
                           initial={'user': current_contest.user.all(), 'problem': current_contest.problem.all(),
                                    'title': current_contest.title})
    return render(request, 'webpages/edit_contest.html', {'form': form, 'current_contest': current_contest,
                                                          'contest': contest})


def load_contest(request):
    contest_id = request.GET.get('code')
    request.session['contest'] = contest_id
    # print(request.session['contest'], contest_id)

    email = request.session.get('user_auth')
    if email:
        contest = contest_filter(request, email)

        return render(request, 'webpages/contest_change_ajax.html', {'contest': contest})


def first_solver(contest_id):
    first_solver_user = {}
    current_contest = Contest.objects.get(pk=contest_id)
    total_problems = current_contest.problem.all()
    for i in total_problems:
        user = set()
        first = Submit.objects.filter(contest=current_contest, submit_time__gte=current_contest.start_time,
                                      submit_time__lte=current_contest.end_time,
                                      result='Correct', problem=i).order_by('submit_time')
        if first:
            min_time = first[0].submit_time
        for j in first:
            if j.submit_time <= min_time:
                user.add(j.user)
            else:
                break
        first_solver_user[i] = user
    return first_solver_user


def view_scoreboard_by_user(request):
    email = request.session.get('user_auth')
    if email:
        utc = pytz.UTC
        date = utc.localize(datetime.now())
        contest_id = request.session.get('contest')
        my = User.objects.get(email=email)
        try:
            current_contest = Contest.objects.get(pk=contest_id)
            contest_title = current_contest.title
        except Contest.DoesNotExist:
            raise Http404("The contest is not registered.")
        contest_start_time = current_contest.start_time
        total_users = current_contest.user.all()
        total_problems = current_contest.problem.all()
        all_submit = Submit.objects.filter(contest=current_contest, submit_time__gte=current_contest.start_time,
                                           submit_time__lte=current_contest.end_time)
        first_solved_questions = first_solver(contest_id)

        submit_vs_user = dict()
        score_vs_user = dict()
        for i in total_users:
            submit_vs_user_vs_problem = dict()
            for j in total_problems:
                submit_vs_user_vs_problem[j] = []
            submit_vs_user[i] = submit_vs_user_vs_problem
            score_vs_user[i] = submit_vs_user_vs_problem

        for i in all_submit:
            submit_vs_user[i.user][i.problem].append(i)

        for _users_key in submit_vs_user:

            _users = submit_vs_user[_users_key]
            for _problems_key in _users:
                _problems = sorted(_users[_problems_key], key=lambda x: x.submit_time, reverse=False)
                _count = 0
                _count_freeze = 0
                _time_taken = -1
                _punish_time = 0
                for _submits in _problems:
                    if date < current_contest.frozen_time or date > current_contest.unfrozen_time or \
                            _submits.submit_time < current_contest.frozen_time \
                            or _submits.submit_time > current_contest.unfrozen_time:
                        if _submits.result == 'Correct':
                            _count += 1
                            td = _submits.submit_time - contest_start_time
                            _time_taken = td.seconds // 60 + td.days * 3600

                            break
                        elif _submits.result == 'Compiler Error':
                            _count += 1
                        else:
                            _count += 1
                            _punish_time += 20
                    else:
                        _count_freeze += 1
                        if _submits.result == 'Correct':
                            break
                score_vs_user[_users_key][_problems_key] = (_count, _time_taken, _time_taken + _punish_time,
                                                            _count_freeze)

        total_score = []
        for _user in score_vs_user:
            score = score_vs_user[_user]
            point = 0
            punish_time = 0
            last_submit = 0
            for _problem_key in score:
                pro = score[_problem_key]

                if pro[0] and pro[1] != -1:
                    punish_time += pro[2]
                    point += 1
                    last_submit = max(last_submit, pro[1])
            total_score.append([point, punish_time, last_submit, _user.name, _user.id, _user])
        total_score.sort(reverse=True)

        total_score[0].append(1)
        for i in range(1, len(total_score)):
            if total_score[i][:3] == total_score[i-1][:3]:
                total_score[i].append('')
            else:
                total_score[i].append(i+1)

        # print(total_score)

        scoreboard = []
        for table in total_score:
            this_user = table[5]
            this_point = str(table[0]) + " " + str(table[1])
            this_point = mark_safe("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join(this_point.split(' ')))
            this_user_name = table[3]
            each = list()
            each.append((table[6], '#ffffff', 30))
            if this_user == my:
                each.append((table[3], '#fa4500', 300))
            else:
                each.append((this_user_name, '#ffffff', 300))
            each.append((this_point, '#ffffff', 100))

            for pro in total_problems:
                each_point = score_vs_user[this_user][pro]
                if each_point[0] == 0:
                    if each_point[3] == 0:
                        each.append((0, '#ffffff', 80))
                    else:
                        each.append((each_point[3], '#00ffff', 80))
                elif each_point[1] == -1:
                    if each_point[3] == 0:
                        each.append((each_point[0], '#cd5c5c', 80))
                    else:
                        each.append((str(each_point[0])+'+'+str(each_point[3]), '#00ffff', 80))
                else:
                    if this_user in first_solved_questions[pro]:
                        each.append((str(each_point[0]) + '/' + str(each_point[1]), '#008000', 80))
                    else:
                        each.append((str(each_point[0])+'/'+str(each_point[1]), '#32cd32', 80))
            scoreboard.append(each)
            # '#008000'
        contest = contest_filter(request, email)
        return render(request, 'webpages/scoreboard_view_by_user.html',
                      {'scoreboard': scoreboard, 'contest': contest, 'contest_title': contest_title,
                       'total_problems': total_problems})

    else:
        raise Http404("You are not logged in")


def load_contest_by_admin(request):
    contest_id = request.GET.get('code')
    request.session['admin_contest'] = contest_id
    email = request.session.get('admin_auth')
    if email:
        admin = Admin.objects.get(email=email)
        utc = pytz.UTC
        date = utc.localize(datetime.now())
        contest = Contest.objects.filter(campus=admin.campus, active_time__lt=date, deactivate_time__gt=date,
                                         enable='yes').order_by('start_time')
        for i in contest:
            if contest_id == str(i.id):
                i.selected = 'yes'
            else:
                i.selected = 'no'

        return render(request, 'webpages/contest_change_ajax.html', {'contest': contest})


def view_scoreboard_by_admin(request):
    email = request.session.get('admin_auth')
    if email:
        admin = Admin.objects.get(email=email)
        utc = pytz.UTC
        date = utc.localize(datetime.now())
        contest_id = request.session.get('admin_contest')
        try:
            current_contest = Contest.objects.get(pk=contest_id)
            contest_title = current_contest.title
        except Contest.DoesNotExist:
            raise Http404("The contest is not registered.")
        contest_start_time = current_contest.start_time
        total_users = current_contest.user.all()
        total_problems = current_contest.problem.all()
        all_submit = Submit.objects.filter(contest=current_contest, submit_time__gte=current_contest.start_time,
                                           submit_time__lte=current_contest.end_time)

        first_solved_questions = first_solver(contest_id)
        submit_vs_user = dict()
        score_vs_user = dict()
        for i in total_users:
            submit_vs_user_vs_problem = dict()
            for j in total_problems:
                submit_vs_user_vs_problem[j] = []
            submit_vs_user[i] = submit_vs_user_vs_problem
            score_vs_user[i] = submit_vs_user_vs_problem

        for i in all_submit:
            submit_vs_user[i.user][i.problem].append(i)

        for _users_key in submit_vs_user:

            _users = submit_vs_user[_users_key]
            for _problems_key in _users:
                _problems = sorted(_users[_problems_key], key=lambda x: x.submit_time, reverse=False)
                _count = 0
                _time_taken = -1
                _punish_time = 0
                for _submits in _problems:
                    if _submits.result == 'Correct':
                        _count += 1
                        td = _submits.submit_time - contest_start_time
                        _time_taken = td.seconds // 60

                        break
                    elif _submits.result == 'Compiler Error':
                        _count += 1
                    else:
                        _count += 1
                        _punish_time += 20
                score_vs_user[_users_key][_problems_key] = (_count, _time_taken, _time_taken + _punish_time)

        total_score = []
        for _user in score_vs_user:
            score = score_vs_user[_user]
            point = 0
            punish_time = 0
            last_submit = 0
            for _problem_key in score:
                pro = score[_problem_key]

                if pro[0] and pro[1] != -1:
                    punish_time += pro[2]
                    point += 1
                    last_submit = max(last_submit, pro[1])
            total_score.append([point, punish_time, last_submit, _user.name, _user.id, _user])
        total_score.sort(reverse=True)

        total_score[0].append(1)
        for i in range(1, len(total_score)):
            if total_score[i][:3] == total_score[i-1][:3]:
                total_score[i].append('')
            else:
                total_score[i].append(i+1)

        print(total_score)

        scoreboard = []
        for table in total_score:
            this_user = table[5]
            this_point = str(table[0]) + " " + str(table[1])
            this_point = mark_safe("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join(this_point.split(' ')))
            this_user_name = table[3]
            each = list()
            each.append((table[6], '#ffffff', 30))
            each.append((this_user_name, '#ffffff', 300))
            each.append((this_point, '#ffffff', 100))

            for pro in total_problems:
                each_point = score_vs_user[this_user][pro]
                if each_point[0] == 0:
                    each.append((0, '#ffffff', 80))
                elif each_point[1] == -1:
                    each.append((each_point[0], '#cd5c5c', 80))
                else:
                    if this_user in first_solved_questions[pro]:
                        each.append((str(each_point[0]) + '/' + str(each_point[1]), '#008000', 80))
                    else:
                        each.append((str(each_point[0])+'/'+str(each_point[1]), '#32cd32', 80))
            scoreboard.append(each)
            # '#008000'
        contest = admin_view_contest_form(request, email)
        return render(request, 'webpages/scoreboard_view_by_admin.html',
                      {'scoreboard': scoreboard, 'contest': contest, 'contest_title': contest_title,
                       'total_problems': total_problems})

    else:
        raise Http404("You are not logged in")

