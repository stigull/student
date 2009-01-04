#coding: utf-8
from django.conf.urls.defaults import *
from django.utils.translation import ugettext as _

from student.views import start_new_schoolyear, show_info

urlpatterns = patterns('',
    url(r'skolaar/(?P<schoolyear_starts>\d{4})-(?P<schoolyear_ends>\d{4})/$', show_info, name = 'info_show_schoolyear'),
    url(r'$', show_info, name = 'info_show')
)

 
