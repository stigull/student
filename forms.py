#coding: utf-8
import django.forms as forms
from django.contrib.formtools.wizard import FormWizard
from django.contrib.localflavor.is_.forms import ISIdNumberField,  ISPostalCodeSelect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from student.models import Schoolyear, Info

TITLES = [_(u"Skrá nýtt skólaár") ]

class SchoolyearWizard(FormWizard):
    def done(self, request, form_list):
        return HttpResponseRedirect(reverse('admin'))
    
    def render_template(self, request, form, previous_fields, step, context=None):
        context = {'title': TITLES[step] }
        return super(SchoolyearWizard, self).render_template(request, form, previous_fields, step,context = context)
    
class InfoForm(forms.ModelForm):
    kennitala = ISIdNumberField(label = _(u'Kennitala'))
    postalcode = forms.CharField(label = _(u'Póstnúmer og borg'), widget = ISPostalCodeSelect())
    
    class Meta:
        model = Info
        
    def clean(self):
        super(InfoForm, self).clean()
        if Info.objects.all().count() > 0 and self.instance is not None and self.instance.id is None:
            raise forms.ValidationError(_(u"Það er aðeins leyfilegt að skrá eitt sett af upplýsingum. Vinsamlegast breytið upplýsingunum sem nú þegar eru til staðar"))
        else:
            return self.cleaned_data
            
        
class SchoolyearForm(forms.ModelForm):
    class Meta:
        model = Schoolyear

    def clean_starts(self):
        oldschoolyear = Schoolyear.objects.filter(starts__year = self.cleaned_data['starts'].year)
        instance = self.instance
        if oldschoolyear.count() > 0 and oldschoolyear[0] != instance:
            raise forms.ValidationError(_(u"Það er til skólaár sem hefst á þessu ári"))
        else:
            return self.cleaned_data['starts']
        
    def clean_ends(self):
        oldschoolyear = Schoolyear.objects.filter(ends__year = self.cleaned_data['ends'].year)
        instance = self.instance
        if oldschoolyear.count() > 0 and oldschoolyear[0] != instance:
            raise forms.ValidationError(_(u"Það er til skólaár sem lýkur á þessu ári"))
        else:
            return self.cleaned_data['ends']
        
    def clean(self):
        super(SchoolyearForm, self).clean()
        if 'starts' in self.cleaned_data and 'ends' in self.cleaned_data:
            starts = self.cleaned_data['starts']
            ends = self.cleaned_data['ends']
            if starts >= ends:
                raise forms.ValidationError(_(u"Skólaárið verður að byrja áður en það endar"))
           
            if ends.year - starts.year != 1:
                raise forms.ValidationError(_(u"Það má ekki vera meira en eitt ár á milli skólaára"))
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data

                            
