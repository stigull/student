#coding: utf-8
from django.contrib import admin

from student.models import Schoolyear, Role, Account, Info, UserInRole
from student.forms import SchoolyearForm, InfoForm
    
class UserInRoleAdmin(admin.TabularInline):
    model = UserInRole
    extra = 3
    
class InfoAdmin(admin.ModelAdmin):
    form = InfoForm
    exclude = ['info_html']

class SchoolyearAdmin(admin.ModelAdmin):
    form = SchoolyearForm
    inlines = [UserInRoleAdmin]
    
for model in [Role, Account, UserInRole]:
    admin.site.register(model) 
    
admin.site.register(Schoolyear, SchoolyearAdmin)
admin.site.register(Info, InfoAdmin)




