#coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.contrib.localflavor.is_.is_postalcodes import IS_POSTALCODES

try:
    from markdown2 import markdown
except ImportError:
    def markdown(string):
        return string

from stigull_profile.models import GOVERNMENT_GROUP

POSTALCODES  = dict(IS_POSTALCODES)

class Schoolyear(models.Model):
    """
    Data invariant:
        starts is the beginning date of the schoolyear
        ends is the final date of the schoolyear

        start and end are unique together, i.e. there can only be one schoolyear that starts in starts and ends in ends

        roles is the set of all UserInRoles objects that this Schoolyear contains
    """
    starts = models.DateField(_(u"Hefst"), help_text = _(u"ÁÁÁÁ-MM-DD"))
    ends = models.DateField(_(u"Lýkur"), help_text = _(u"ÁÁÁÁ-MM-DD"))

    class Meta:
        unique_together = [('starts', 'ends')]
        ordering = ['-starts']
        get_latest_by = ('starts',)
        verbose_name = _(u"Skólaár")
        verbose_name_plural = _(u"Skólaár")

    def __unicode__(self):
        return "%s - %s" %(self.starts.year, self.ends.year)

    def get_absolute_url(self):
        return ('info_show_schoolyear', (), {'schoolyear_starts' : self.starts.year, 'schoolyear_ends': self.ends.year })
    get_absolute_url = models.permalink(get_absolute_url)

    def has_laws(self):
        """
        Usage:  has_laws = schoolyear.has_laws()
        After:  has_laws is True if and only if the schoolyear has an associated Laws object
        """
        try:
            return self.laws.all().count() == 1
        except AttributeError:
            return False

class Account(models.Model):
    name = models.CharField(_(u'Nafn'), max_length=50)
    number = models.CharField(_(u'Reikningsnr.'), max_length=30)

    class Meta:
        verbose_name = _(u"Reikningur")
        verbose_name_plural = _(u"Reikningar")

    def __unicode__(self):
        return "%s : %s" % (self.name, self.number)

class Info(models.Model):
    """

    Data invariant:
        name is the name of the student association
        kennitala is the social security number of the student assciation
        address is the physical address of the student association
        postalcode is the postalcode of the student associtation
        email is the email of the student association
        accounts are the accounts of the student association
        info is the information text about the student association
        info_html is the html version of info


    """
    name = models.CharField(_(u'Nafn félagsins'), max_length = 200)
    kennitala = models.CharField(_(u'Kennitala'),max_length=11)
    address = models.CharField(_(u'Heimilisfang'), max_length=255)
    postalcode = models.CharField(_(u'Póstnúmer'), max_length=3)
    email = models.EmailField(_(u'Tölvupóstfang'))
    accounts = models.ManyToManyField(Account, verbose_name=_(u'Reikningar'), blank=True)
    info = models.TextField(_(u'Um félagið'), blank=True, help_text = _(u"Notið Markdown rithátt fyrir HTML"))
    info_html = models.TextField(blank=True)

    class Meta:
        verbose_name = _(u"Upplýsingar")
        verbose_name_plural = _(u"Upplýsingar")
        get_latest_by = ('id',)

    def get_absolute_url(self):
        #TODO: URL
        return ""

    def get_postalcode_and_city(self):
        """
        Usage:  postalcode_and_city = info.get_postalcode_and_city()
        After:  postalcode_and_city is the postalcode and city of the student association
        """
        return POSTALCODES[self.postalcode]

    def get_city(self):
        return " ".join(self.get_postalcode_and_city().split(" ")[1:])
    city = property(get_city)

    def get_kennitala(self):
        return self.kennitala.replace("-", "")

    def save(self):
        self.info_html = markdown(self.info)
        super(Info, self).save()

    def __unicode__(self):
        return "%s: %s/%s" % (self.name, self.kennitala, self.email)

class Role(models.Model):
    name = models.CharField(_(u"Nafn embættis"), max_length=40, unique=True)
    is_president = models.BooleanField(_(u"Er æðsta embætti innan félagsins"), blank = True)
    is_part_of_government = models.BooleanField(_(u"Er stjórnarembætti"), blank=True)

    class Meta:
        verbose_name = _(u"Embætti")
        verbose_name_plural = _(u"Embætti")
        ordering = ('name', 'is_part_of_government')

    def __unicode__(self):
        return self.name

class GovernmentManager(models.Manager):
    """
    A manager who only queries users in the student government
    """

    def get_query_set(self):
        return super(GovernmentManager, self).get_query_set().filter(role__is_part_of_government = True)

    def get_government(self, schoolyear = None):
        """
        Usage:  government = UserInRole.government.get_government([schoolyear =None])
        Before: schoolyear is a Schoolyear instance or None and then default to the current Schoolyear
        After:  government is a queryset of UserInRole objects and every such object
                represents a role in the government in schoolyear
        """
        if schoolyear is None:
            schoolyear = Schoolyear.objects.latest()
        return self.get_query_set().filter(schoolyear = schoolyear)

    def get_presidential_government(self, schoolyear = None):
        return self.get_government(schoolyear).filter(role__is_president = True)

    def get_non_presidential_government(self, schoolyear = None):
        return self.get_government(schoolyear).filter(role__is_president = False)

class NonGovernmentManager(models.Manager):
    """
    A manager who only queries users who are not in the student government
    """

    def get_query_set(self):
        return super(NonGovernmentManager, self).get_query_set().filter(role__is_part_of_government = False)


class UserInRole(models.Model):
    """
    Represents the hierarchy of roles in the student administration in a certain schoolyear, i.e. connects user with roles

    Data invariant:
        schoolyear is the schoolyear in which user had the role
        user is the user who had the role
        role is the role of the user

        government is a manager who queries only the student government
        non_government is a manager who queries only roles not in the student government
    """
    schoolyear = models.ForeignKey(Schoolyear, related_name = "roles")
    user = models.ForeignKey("auth.User", related_name = 'roles')
    role = models.ForeignKey(Role)

    objects = models.Manager()
    government = GovernmentManager()
    non_government = NonGovernmentManager()

    class Meta:
        unique_together = [('schoolyear','user', 'role')]
        verbose_name = _(u"Nemandi í embætti á skólaári")
        verbose_name_plural = _(u"Nemendur í embættum á skólaári")

    def __unicode__(self):
        try:
            return "%s : %s - %s" % (self.schoolyear, self.role.name, self.user.get_profile().get_fullname())
        except:
            return "%s : %s - %s" % (self.schoolyear, self.role.name, self.user.username)

def add_user_to_government(sender, instance, created, raw, **kwargs):
    """ Adds the user to the group Stjórn if the role is a governmental role """
    if instance.role.is_part_of_government and created:
        government = Group.objects.get(name = GOVERNMENT_GROUP)
        instance.user.groups.add(government)

def remove_user_from_government(sender, instance,**kwargs):
    """ Removes the user from the group Stjórn if the role is a governmental role """
    if instance.role.is_part_of_government:
        government = Group.objects.get(name = GOVERNMENT_GROUP)
        instance.user.groups.remove(government)


models.signals.post_save.connect(add_user_to_government, sender = UserInRole)
models.signals.pre_delete.connect(remove_user_from_government, sender = UserInRole)
