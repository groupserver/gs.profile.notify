# coding=utf-8
from zope.component import createObject, adapts
from zope.cachedescriptors.property import Lazy
from zope.interface import implements
from Products.XWFCore.XWFUtils import get_support_email
from Products.CustomUserFolder.interfaces import ICustomUser, IGSUserInfo
from gs.profile.email.base.emailuser import EmailUser
from interfaces import IGSNotifyUser
from audit import Auditor, SEND_NOTIFICATION, SEND_MESSAGE
from gs.email import send_email

import logging
log = logging.getLogger("gs.profile.notify.notifyuser")

class NotifyUser(object):
    implements( IGSNotifyUser )
    adapts( ICustomUser )

    def __init__(self, user, siteInfo=None):
        self.user = user
        self.siteInfo = siteInfo
        if not self.siteInfo:
            self.siteInfo = createObject('groupserver.SiteInfo', user)

    @Lazy
    def emailUser(self):
        userInfo = IGSUserInfo(self.user)
        retval = EmailUser(self.user, userInfo)
        return retval
    
    @Lazy
    def auditor(self):
        retval = Auditor(self.siteInfo, self.user)
        return retval
        
    @Lazy
    def addresses(self):
        retval = [e.lower() for e in self.emailUser.get_addresses()]
        return retval

    @property
    def emailTemplates(self):
        sr = self.user.site_root()
        assert sr
        retval = sr.Templates.email.notifications.aq_explicit
        return retval
    
    def get_addresses(self, email_only=()):
        if email_only:
            toAddrs = [e.lower() for e in email_only]
            retval = [e for e in self.addresses if e.lower() in toAddrs]
        else:
            retval = [e.lower() for e in self.emailUser.get_verified_addresses()]
        assert type(retval) == list
        log.warn('%s has no email addresses to send the notification to.' %
             self.user.getId())
        return retval
    
    def send_notification(self, n_type, n_id='default', n_dict=None, email_only=()):
        if not n_dict:
            n_dict = {}
        self.auditor.info(SEND_NOTIFICATION, n_type, n_id)
        for address in self.get_addresses(email_only):
            msg = self.render_notification(n_type, n_id, n_dict, address)
            if msg:
                self.send_message(msg, address)
                     
    def send_message(self, message, email_to, email_from=''):
        assert email_to.lower() in self.addresses, \
            '%s is not an address for %s' % (email_to, self.user.getId())
        if not email_from:
            email_from = get_support_email(self.user, self.siteInfo.id)
        self.auditor.info(SEND_MESSAGE, str(len(message)), email_to)
        send_email(email_from, email_to, message)
        
    def render_notification(self, n_type, n_id, n_dict, email_address):
        """Generate a notification, returning it as a string."""
        ptype_templates = getattr(self.emailTemplates, n_type, None)
        assert ptype_templates, 'No template of type "%s" found' % n_type
        ignore_ids = getattr(ptype_templates, 'ignore_ids', [])
        if n_id in ignore_ids:
            return None
        
        template = (getattr(ptype_templates.aq_explicit, n_id, None) or
                    getattr(ptype_templates.aq_explicit, 'default', None))
        assert template, 'No template found for %s/%s' % (n_type, n_id)
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
        NotifyUser.__init__(self, userInfo.user)

