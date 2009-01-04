#coding: utf-8
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from student.forms import SchoolyearWizard, SchoolyearForm 
from student.models import Info, Schoolyear, UserInRole

def start_new_schoolyear(request):
    return SchoolyearWizard([SchoolyearForm])(request)
start_new_schoolyear = staff_member_required(start_new_schoolyear)


def show_info(request, schoolyear_starts = None, schoolyear_ends = None):
    context = {}
    try:
        context['info'] = Info.objects.latest() #There is always only one Info
    except Info.DoesNotExist:
        #TODO: Hérna ætti að láta vefstjóra vita af því að það séu engar upplýsingar skráðar
        pass
    
    if schoolyear_starts is None and schoolyear_ends is None:
        try:
            schoolyear = Schoolyear.objects.latest()
        except Schoolyear.DoesNotExist:
            #TODO: Hérna ætti að láta vefstjóra vita af því að það sé ekkert skólaár skráð
            return HttpResponseRedirect(reverse('index'))
    else:
        schoolyear = get_object_or_404(Schoolyear, starts__year = schoolyear_starts, ends__year = schoolyear_ends)
    
    context['schoolyear'] = schoolyear
    context['government'] = UserInRole.government.get_government(schoolyear = schoolyear)
    context['non_government'] = UserInRole.non_government.all()
    return  render_to_response('info/info_base.html', context , context_instance = RequestContext(request))
    