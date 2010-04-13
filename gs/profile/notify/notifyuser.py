# coding=utf-8
from zope.component import createObject, adapts
from zope.interface import implements, implementedBy
from Products.XWFCore.XWFUtils import get_support_email
from Products.CustomUserFolder.interfaces import ICustomUser, IGSUserInfo
from interfaces import IGSNotifyUser

class NotifyUser(object):
    implements( IGSNotifyUser )
    adapts( ICustomUser )

    def __init__(self, user):
        self.user = user
        self.siteInfo = createObject('groupserver.SiteInfo', user)
        self.__addresses = self.__emailTemplates = self.__mailhost = None

    @property
    def addresses(self):
        if self.__addresses == None:
            self.__addresses = [e.lower() for e in 
                                self.user.get_emailAddresses()]
        return self.__addresses

    @property
    def mailhost(self):
        if self.__mailhost == None:
            sr = self.user.site_root()
            try:
                self.__mailhost = sr.superValues('Mail Host')[0]
            except:
                raise AttributeError, "Can't find a Mail Host object"
        return self.__mailhost
        
    @property
    def emailTemplates(self):
        if self.__emailTemplates == None:
            sr = self.user.site_root()
            assert sr
            self.__emailTemplates = sr.Templates.email.notifications.aq_explicit
        return self.__emailTemplates
    
    def get_addresses(self, email_only=()):
        if email_only:
            toAddrs = [e.lower() for e in email_only]
            retval = [e for e in self.addresses if e.lower() in toAddrs]
        else:
            retval = [e.lower() for i in self.user.get_verifiedEmailAddresses()]
        assert type(retval) == list
        assert retval, 'No email addresses to send the notification to.'
        return retval
    
    def send_notification(self, n_type, n_id='default', n_dict=None, email_only=()):
        if not n_dict:
            n_dict = {}
        # TODO Audit
        for address in self.get_addresses(email_only):
            msg = self.render_notification(n_type, n_id, n_dict, address)
            self.send_message(msg, address)
                     
    def send_message(self, message, email_to, email_from=''):
        assert email_to in self.addresses, \
            '%s is not an address for %s' % (email_to, self.user.getId())
        if not email_from:
            email_from = get_support_email(self.user, self.siteInfo.id)
        # TODO: Audit
        self.mailhost._send(mfrom=email_from, mto=email_to, 
                            messageText=message)
        
    def render_notification(self, n_type, n_id, n_dict, email_address):
        """Generate a notification, returning it as a string."""
        ptype_templates = getattr(self.emailTemplates, n_type, None)
        assert ptype_templates, 'No template of type "%s" found' % n_type
        ignore_ids = getattr(ptype_templates, 'ignore_ids', [])
        if n_id in ignore_ids:
            return None
        
        template = (getattr(ptype_templates.aq_explicit, n_id, None) or
                    getattr(ptype_templates.aq_explicit, 'default', None))
        assert template, 'No template found'
        # --=mpj17=-- changed self.REQUEST to None
        retval = template(self.user, None, to_addr=email_address, 
                            n_id=n_id, n_type=n_type, n_dict=n_dict)
        if isinstance(retval, unicode):
            retval = retval.encode('utf-8','ignore')
        assert type(retval) == str
        return retval

class NotifyUserFromUserInfo(NotifyUser):
    implements( IGSNotifyUser )
    adapts( IGSUserInfo )

    def __init__(self, userInfo):
        NotifyUser.__init__(userInfo.user)

