# coding=utf-8
from email.Header import Header
from Products.CustomUserFolder.interfaces import IGSUserInfo
from gs.profile.email.base.emailuser import EmailUser

utf8='utf-8'

def addr_hdr_val(displayName, addrSpec):
    # --=mpj17=--
    #  See `RFC2047 <http://tools.ietf.org/html/rfc2047>`_ and
    # `RFC5322 http://tools.ietf.org/html/rfc5322#section-3.4>`_.
    encodedWord = str(Header(displayName, utf8))
    if encodedWord == displayName:
        # RFC5322: display-name = phrase; phrase = word; word = quoted-string
        phrase = '"%s"' % encodedWord
    else:
        # RFC2047: An 'encoded-word' MUST NOT appear within a 'quoted-string'.
        phrase = encodedWord
    angleAddr = '<%s>' % addrSpec # By itself, an angle address should never appear.
    nameAddr = '%s %s' % (phrase, angleAddr) # I use a space as the CFWS
    return nameAddr

class Addressee(object):
    def __init__(self, userInfo, address):
        self.userInfo = userInfo
        self.addr = address.strip()
        eu = EmailUser(userInfo.user, userInfo)
        userAddrs = [l.lower() for l in eu.get_addresses()]
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
        email = self.siteInfo.get_support_email()
        displayName = u'%s Support' % self.siteInfo.name
        retval = addr_hdr_val(displayName, email)
        assert retval
        return retval

    def __str__(self):
        retval = str(self.header)
        assert retval
        return retval
