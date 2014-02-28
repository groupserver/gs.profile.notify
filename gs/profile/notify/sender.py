# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.utils import formataddr
from zope.i18nmessageid import MessageFactory
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
_ = MessageFactory('groupserver')
from gs.core import to_unicode_or_bust
from gs.profile.email.base.emailuser import EmailUser
from Products.CustomUserFolder.interfaces import IGSUserInfo
from .audit import Auditor, CREATE_MESSAGE
from .notifyuser import NotifyUser
UTF8 = 'utf-8'


class MessageSender(object):
    def __init__(self, context, toUserInfo):
        self.context = context
        self.toUserInfo = toUserInfo

    @Lazy
    def emailUser(self):
        assert self.context
        assert self.toUserInfo
        retval = EmailUser(self.context, self.toUserInfo)
        assert retval, 'Could not create the email-user'
        return retval

    @Lazy
    def siteInfo(self):
        assert self.context
        retval = createObject('groupserver.SiteInfo', self.context)
        assert retval, 'Could not create the site info'
        return retval

    def send_message(self, subject, txtMessage, htmlMessage='',
                        fromAddress=None, toAddresses=None):
        msg = self.create_message(subject, txtMessage, htmlMessage,
                                  fromAddress, toAddresses)
        notifyUser = NotifyUser(self.toUserInfo.user)
        if not toAddresses:
            toAddresses = self.emailUser.get_delivery_addresses()
        fromAddr = self.from_address(fromAddress)
        for addr in toAddresses:
            notifyUser.send_message(msg, addr, fromAddr)

    def create_message(self, subject, txtMessage, htmlMessage,
                        fromAddress, toAddresses):

        auditor = Auditor(self.siteInfo, self.toUserInfo)
        auditor.info(CREATE_MESSAGE, subject)

        container = MIMEMultipart('alternative')
        container['Subject'] = str(Header(subject, UTF8))
        container['From'] = self.from_header_from_address(fromAddress)
        container['To'] = self.to_header_from_addresses(toAddresses)

        # FIXME: The txtMessage argument should not have to be encoded.
        txt = MIMEText(txtMessage.encode(UTF8), 'plain', UTF8)
        container.attach(txt)

        if htmlMessage:
            # --=mpj17=-- I checked, and it is valid to have a
            # multipart message with only one part: "The body must then
            # contain one or more body parts\ldots"
            # <http://tools.ietf.org/html/rfc2046#section-5.1>
            html = MIMEText(htmlMessage.encode(UTF8), 'html', UTF8)
            container.attach(html)
        retval = container.as_string()
        assert retval
        return retval

    def from_address(self, address):
        if address:
            retval = address
        else:
            retval = self.siteInfo.get_support_email()
        return retval

    @classmethod
    def get_addr_line(cls, name, addr):
        # --=mpj17=-- In Python 3 just using formataddr, sans the Header, will
        #  work. This method should be removed.
        unicodeName = to_unicode_or_bust(name)
        headerName = Header(unicodeName, UTF8)
        encodedName = headerName.encode()
        retval = formataddr((encodedName, addr))
        return retval

    def from_header_from_address(self, address):
        if address:
            u = self.context.acl_users.get_userByEmail(address)
            assert u, 'Could not find user for <%s>' % address
            userInfo = IGSUserInfo(u)
            retval = self.get_addrr_line(userInfo.name, address)
        else:
            name = self.siteInfo.name + _(' Support')
            email = self.siteInfo.get_support_email()
            retval = self.get_addr_line(name, email)
        assert retval
        return retval

    def to_header_from_addresses(self, addresses):
        if not addresses:
            addresses = self.emailUser.get_delivery_addresses()
        assert addresses, 'No addresses for %s (%s)' % \
            (self.toUserInfo.name, self.toUserInfo.id)
        fn = self.toUserInfo.name.encode(UTF8)
        retval = ', '.join([self.get_addr_line(fn, a) for a in addresses])
        assert retval
        return retval
