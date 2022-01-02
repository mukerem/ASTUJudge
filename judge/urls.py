"""bookstore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.homepage, name='home'),
    path('homepage/', views.homepage, name='home'),
    path('admin-register/', views.admin_register, name='admin_register'),
    path('user-register/', views.user_register, name='user_register'),
    path('login/', views.login, name='login'),
    path('user-homepage/', views.user_homepage, name='user_homepage'),

    path('overview/', views.submit_answer, name='submit_answer'),
    path('logout/<role>/', views.logout, name='logout'),
    path('user-profile/', views.view_user_profile, name='user_profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('change-password/<role>/', views.change_password, name='ChangePassword'),
    path('admin-profile/', views.view_admin_profile, name='admin_profile'),
    path('admin-homepage/', views.admin_homepage, name='admin_homepage'),
    path('add-problem/', views.add_problem, name='add_problem'),
    path('add-user/', views.add_user, name='add_user'),
    path('admin-view-user/', views.user_view_by_admin, name='user_view_by_admin'),
    path('not-delete/<page>/', views.not_delete, name='NotDelete'),
    path('delete-user-confirm/<user_id>/', views.delete_user_confirm, name='DeleteUserConfirm'),
    path('delete-user/<user_id>/', views.delete_user, name='DeleteUser'),
    path('view-problem-by-admin/', views.view_problem_by_admin, name='view_problem_by_admin'),
    path('delete-problem-confirm/<problem_id>/', views.delete_problem_confirm, name='delete_problem_confirmation'),
    path('delete-problem/<problem_id>/', views.delete_problem, name='DeleteProblem'),
    path('edit-problem/<problem_id>/', views.edit_problem, name='edit_problem'),
    path('add-sample/<problem_id>/', views.add_sample, name='add_sample'),
    path('delete-test-case-confirm/<test_case_id>/', views.delete_test_case_confirm,
         name='delete_test_case_confirmation'),
    path('delete-test-case/<test_case_id>/', views.delete_test_case, name='delete_test_case'),
    path('view-submission/', views.view_submission, name='view_submission'),
    path('view-problem-by-user/', views.view_problem_by_user, name='view_problem_by_user'),
    path('add-contest/', views.add_contest, name='add_contest'),
    path('view-contest-by-admin/', views.view_contest_by_admin, name='view_contest_by_admin'),
    path('delete-contest-confirm/<contest_id>/', views.delete_contest_confirm, name='delete_contest_confirmation'),
    path('delete-contest/<contest_id>/', views.delete_contest, name='DeleteContest'),
    path('edit-contest/<contest_id>/', views.edit_contest, name='edit_contest'),
    path('view-contest/<contest_id>/', views.edit_contest, name='view_contest_by_user'),
    path('load-contest/', views.load_contest, name='ajax_load_contest'),
    path('view-scoreboard-by-user/', views.view_scoreboard_by_user, name='view_scoreboard_by_user'),
    path('load-contest-by-admin/', views.load_contest_by_admin, name='ajax_load_contest_by_admin'),
    path('view-scoreboard-by-admin/', views.view_scoreboard_by_admin, name='view_scoreboard_by_admin'),
]

