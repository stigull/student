#coding:utf-8
 
from student.models import Info

def info_name_processor(request):
    try:
        info = Info.objects.all().values('name', 'email')[0]
    except IndexError:
        #TODO: Logga
        return {'info_name' : '', 'info_email' : '' }
    return {'info_name': info['name'], 'info_email': info['email'] }
