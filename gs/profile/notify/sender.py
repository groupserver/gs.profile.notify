# coding=utf-8
from email.Message import Message
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.utils import formataddr
from Products.CustomUserFolder.interfaces.IGSUserInfo
from notifyuser import NotifyUser

class MessageSender(object):
    def __init__(self, context, toUserInfo):
        self.context = context
        self.toUserInfo = toUserInfo
        self.notifyUser = NotifyUser(toUserInfo.userObj)
        
    def send_message(self, subject, txtMessage, htmlMessage='', 
                        fromAddress=None, toAddresses=None):
        msg = self.create_message(subject, txtMessage, htmlMessage, 
                                  fromAddress, toAddresses)
        if not toAddresses:
            toAddresses = self.notifyUser.addresses
        t = msg.as_string()
        for addr in toAddresses:
            self.notifyUser.send_message(t, addr, fromAddress)
            
    def create_message(self, subject, txtMessage, htmlMessage, 
                        fromAddress, toAddresses):
        container = MIMEMultipart('alternative')
        container['Subject'] = str(Header(subject, utf8))
        container['From'] = self.from_header_from_address(fromAddress)
        container['To'] = self.to_header_from_addresses(toAddresses)

        txt = MIMEText(t.encode(utf8), 'plain', utf8)
        container.attach(txt)
        
        if htmlMessage:
            html = MIMEText(htmlMessage.encode(utf8), 'html', utf8)
            container.attach(html)

        return container

    def from_header_from_address(self, address):
        # TODO: support if address is none
        u = self.context.acl_users.get_userByEmail(address)
        assert u, 'Could not find user for <%s>' % address
        userInfo = IGSUserInfo(u)
        retval = formataddr((userInfo.name, address))
        assert retval
        return retval

    def to_header_from_addresses(self, addresses):
        if not addresses:
            addresses = self.notifyUser.addresses
        assert addresses, 'No addresses for %s (%s)' % \
            (self.toUserInfo.name, self.toUserInfo.id)
        fn = self.toUserInfo.name
        retval = ', '.join([formataddr((fn, a)) for a in addresses])
        assert retval
        return retval

