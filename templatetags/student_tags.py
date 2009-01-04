#coding: utf-8

from django import template

from student.models import Schoolyear

register = template.Library()

def get_latest_schoolyear(parser, token):
    """
    Usage:  {% get_latest_schoolyear as varname %}
    After:  varname contains the latest_schoolyear
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError("%s tag takes two arguments" % bits[0])
    
    if bits[1] != 'as':
       raise template.TemplateSyntaxError("First argument for %s must be 'as'" % bits[0])

    return GetSchoolyearNode(varname = bits[2])

class GetSchoolyearNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        try:
            schoolyear = Schoolyear.objects.get_latest()
        except Schoolyear.DoesNotExist:
            schoolyear = None
        context[self.varname] = schoolyear
        return ''
    
register.tag('get_latest_schoolyear', get_latest_schoolyear) 

