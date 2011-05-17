# coding=utf-8
from email.Message import Message
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.utils import formataddr
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groupserver')
from Products.XWFCore.XWFUtils import get_support_email
from Products.CustomUserFolder.interfaces import IGSUserInfo
from notifyuser import NotifyUser
utf8 = 'utf-8'

class MessageSender(object):
    def __init__(self, context, toUserInfo):
        self.context = context
        self.toUserInfo = toUserInfo
        self.notifyUser = NotifyUser(toUserInfo.user)
        
    def send_message(self, subject, txtMessage, htmlMessage='', 
                        fromAddress=None, toAddresses=None):
        msg = self.create_message(subject, txtMessage, htmlMessage, 
                                  fromAddress, toAddresses)
        if not toAddresses:
            toAddresses = self.notifyUser.addresses
        for addr in toAddresses:
            self.notifyUser.send_message(msg, addr, fromAddress)
            
    def create_message(self, subject, txtMessage, htmlMessage, 
                        fromAddress, toAddresses):
        container = MIMEMultipart('alternative')
        container['Subject'] = str(Header(subject, utf8))
        container['From'] = self.from_header_from_address(fromAddress)
        container['To'] = self.to_header_from_addresses(toAddresses)

        txt = MIMEText(txtMessage.encode(utf8), 'plain', utf8)
        container.attach(txt)
        
        if htmlMessage:
            # --=mpj17=-- I checked, and it is valid to have a 
            # multipart message with only one part: "The body must then 
            # contain one or more body parts\ldots"
            # <http://tools.ietf.org/html/rfc2046#section-5.1>
            html = MIMEText(htmlMessage.encode(utf8), 'html', utf8)
            container.attach(html)
        retval = container.as_string()
        assert retval
        return retval

    def from_header_from_address(self, address):
        if address:
            u = self.context.acl_users.get_userByEmail(address)
            assert u, 'Could not find user for <%s>' % address
            userInfo = IGSUserInfo(u)
            retval = formataddr((userInfo.name.encode(utf8), address))
        else:
            siteInfo = createObject('groupserver.SiteInfo', self.context)
            siteId = siteInfo.id
            assert siteId, 'Could not get the site ID'
            name = siteInfo.name +_(' Support')
            email = get_support_email(self.context, siteId)
            retval = formatadddr((name.encode(utf8), email))
        assert retval
        return retval

    def to_header_from_addresses(self, addresses):
        if not addresses:
            addresses = self.notifyUser.addresses
        assert addresses, 'No addresses for %s (%s)' % \
            (self.toUserInfo.name, self.toUserInfo.id)
        fn = self.toUserInfo.name.encode(utf8)
        retval = ', '.join([formataddr((fn.encode(utf8), a)) 
                            for a in addresses])
        assert retval
        return retval

