 
from django.test import TestCase

from student.models import Info
from student.forms import InfoForm

INFO_DATA = {'name' : 'Rabison',
                'kennitala' : '4409922779',
                'address': 'Travisonville',
                'postalcode' : '108',
                'email' : 'rabison@travis.is' }

class TestStudentInfo(TestCase):
    
    def test_create_info(self):
        """ Creates a Info object """
        form = InfoForm(data = INFO_DATA)
        self.assert_(form.is_valid() == True)
             
    def test_multiple_info(self):
        """ Tries to add two different infos """

        info = Info(**INFO_DATA)
        info.save()
        
        form = InfoForm(data = INFO_DATA)   
        self.assert_(form.is_valid() == False)
                            
