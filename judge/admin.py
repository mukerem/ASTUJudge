from django.contrib import admin
from .models import Problem, TestCase, SubmitOutput, User, Submit, Campus, Admin, Contest
from .forms import ContestRegister
# Register your models here.


class CampusAdmin(admin.ModelAdmin):
    fields = ('name', 'logo_tag', 'logo', 'country', 'flag_tag', 'flag')
    readonly_fields = ('logo_tag', 'flag_tag')


class UserAdmin(admin.ModelAdmin):
    fields = ('name', 'middle_name', 'last_name', 'phone', 'email', 'sex', 'password', 'image_tag', 'photo', 'campus',
              'register_date')
    readonly_fields = ('image_tag',)


class AdminAdmins(admin.ModelAdmin):
    fields = ('name', 'middle_name', 'last_name', 'phone', 'email', 'sex', 'password', 'image_tag', 'photo', 'campus',
              'register_date')
    readonly_fields = ('image_tag',)


class ContestAdmins(admin.ModelAdmin):
    fields = ('title', 'active_time', 'start_time', 'end_time', 'frozen_time', 'unfrozen_time', 'deactivate_time',
              'problem', 'user', 'image_tag', 'photo', 'campus', 'enable', 'register_date')
    readonly_fields = ('image_tag',)


admin.site.register(Campus, CampusAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Admin, AdminAdmins)
admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(SubmitOutput)
admin.site.register(Submit)
admin.site.register(Contest, ContestAdmins)
