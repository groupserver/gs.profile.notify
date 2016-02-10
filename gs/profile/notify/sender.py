# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
from __future__ import absolute_import, unicode_literals
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.utils import formataddr
from zope.i18nmessageid import MessageFactory
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
_ = MessageFactory('groupserver')
from gs.core import (to_unicode_or_bust, curr_time)
from gs.profile.email.base.emailuser import EmailUser
from Products.CustomUserFolder.interfaces import IGSUserInfo
from .audit import Auditor, CREATE_MESSAGE
from .notifyuser import NotifyUser
UTF8 = 'utf-8'


class MessageSender(object):
    def __init__(self, context, toUserInfo):
        self.context = context
        self.toUserInfo = toUserInfo
        assert self.context
        assert self.toUserInfo

    @Lazy
    def emailUser(self):
        retval = EmailUser(self.context, self.toUserInfo)
        assert retval, 'Could not create the email-user'
        return retval

    @Lazy
    def siteInfo(self):
        retval = createObject('groupserver.SiteInfo', self.context)
        assert retval, 'Could not create the site info'
        return retval

    def send_message(self, subject, txtMessage, htmlMessage='',
                     fromAddress=None, toAddresses=None):
        msg = self.create_message(subject, txtMessage, htmlMessage,
                                  fromAddress, toAddresses)
        notifyUser = NotifyUser(self.toUserInfo.user)
        toAddrs = self.to_addresses(toAddresses)
        fromAddr = self.from_address(fromAddress)
        for addr in toAddrs:
            notifyUser.send_message(msg, addr, fromAddr)

    def create_message(self, subject, txtMessage, htmlMessage,
                       fromAddress, toAddresses):
        auditor = Auditor(self.siteInfo, self.toUserInfo)
        auditor.info(CREATE_MESSAGE, subject)

        container = MIMEMultipart('alternative')
        container['Subject'] = str(Header(subject, UTF8))
        container['From'] = self.from_header_from_address(fromAddress)
        container['To'] = self.to_header_from_addresses(toAddresses)
        container['Date'] = curr_time().strftime('%a, %d %b %Y %H:%M:%S %z')

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

    def to_addresses(self, addresses):
        '''Ensure we have the :mailheader:`To` addresses

:param list addresses: The addresses.
:returns: The ``addresses`` if it is ``True``, or the default delivery-address for the user
          otherwise.
:rtype: list

This method ensures that we always set the :mailheader:`To` addresses'''
        retval = addresses
        if not addresses:
            retval = self.emailUser.get_delivery_addresses()
        return retval

    def from_address(self, address):
        '''Ensure we have a :mailheader:`From` address

:param str address: The address.
:returns: The ``address`` if it is ``True``, or the default support email address otherwise.
:rtype: str

Through ignorance or malace we occasionally are passed no From address. This method ensures that
we always set it'''
        retval = address
        if not address:
            retval = self.siteInfo.get_support_email()
        return retval

    @staticmethod
    def get_addr_line(name, addr):
        '''Get the address line

:param str name: The display-name in the address.
:param str addr: The actual email address.
:returns: A correctly formatted mail header.
:rtype: str'''
        # --=mpj17=-- In Python 3 just using formataddr, sans the Header,
        #  will work. This method should be removed.
        unicodeName = to_unicode_or_bust(name)
        headerName = Header(unicodeName, UTF8)
        encodedName = headerName.encode()
        retval = formataddr((encodedName, addr))
        return retval

    def from_header_from_address(self, address):
        if address:
            name = ''
            u = self.context.acl_users.get_userByEmail(address)
            if u:
                userInfo = IGSUserInfo(u)
                name = userInfo.name
            retval = self.get_addr_line(name, address)
        else:  # not(address)
            name = to_unicode_or_bust(self.siteInfo.name) + _(' Support')
            email = self.siteInfo.get_support_email()
            retval = self.get_addr_line(name, email)
        assert retval
        return retval

    def to_header_from_addresses(self, addresses):
        addrs = self.to_addresses(addresses)
        if not addrs:
            m = 'No addresses for {0} ({1})'
            msg = m.format(self.toUserInfo.name, self.toUserInfo.id)
            raise ValueError(msg)
        fn = self.toUserInfo.name.encode(UTF8)
        retval = ', '.join([self.get_addr_line(fn, a) for a in addrs])
        assert retval
        return retval
