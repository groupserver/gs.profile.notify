# coding=utf-8
from Products.CustomUserFolder.interfaces import ICustomUser, IGSUserInfo
from email.Header import Header
from Products.XWFCore.XWFUtils import get_support_email

utf8='utf-8'

def addr_hdr_val(displayName, addrSpec):
    retval =  u'"%s" <%s>' % (str(Header(displayName, utf8)), addrSpec)
    return retval

class Addressee(object):
    def __init__(self, userInfo, address):
        self.userInfo = userInfo
        self.addr = address.strip()
        userAddrs = [l.lower() for l in userInfo.user.get_emailAddresses()]
        assert address.lower() in userAddrs, '%s not in %s' % \
            (address.lower(), userAddrs)

    @property
    def header(self):
        retval = addr_hdr_val(self.userInfo.name, self.addr)
        assert retval
        return retval

    def __str__(self):
        retval = str(self.header)
        assert retval
        return retval
        
class AddresseeFromCustomUser(Addressee):
    def __init__(self, customUser, address):
        userInfo = IGSUserInfo(customUser)
        Addressee.__init__(self, userInfo, address)

class SupportAddressee(object):
    def __init__(self, context, siteInfo):
        self.siteInfo = siteInfo
        self.context = context
        
    @property
    def header(self):
        email = get_support_email(self.context, self.siteInfo.id)
        displayName = u'%s Support' % self.siteInfo.name
        retval = addr_hdr_val(displayName, email)
        assert retval
        return retval

    def __str__(self):
        retval = str(self.header)
        assert retval
        return retval

