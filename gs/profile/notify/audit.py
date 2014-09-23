# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
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
from pytz import UTC
from datetime import datetime
from zope.component.interfaces import IFactory
from zope.interface import implementer, implementedBy
from gs.core import to_ascii, to_unicode_or_bust
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSAuditTrail import (IAuditEvent, BasicAuditEvent,
                                   AuditQuery, event_id_from_data)
SUBSYSTEM = 'gs.profile.notify'
import logging
log = logging.getLogger(SUBSYSTEM)

UNKNOWN = '0'
SEND_NOTIFICATION = '1'
SEND_MESSAGE = '2'
CREATE_MESSAGE = '3'


@implementer(IFactory)
class AuditEventFactory(object):
    title = 'User Profile Notification Audit-Event Factory'
    description = 'Creates a GroupServer audit event for notifications'

    def __call__(self, context, event_id, code, date, userInfo,
                 instanceUserInfo, siteInfo, groupInfo=None,
                 instanceDatum='', supplementaryDatum='', subsystem=''):

        if (code == SEND_NOTIFICATION):
            event = SendNotificationEvent(context, event_id, date,
                                          userInfo, siteInfo,
                                          instanceDatum,
                                          supplementaryDatum)
        elif (code == SEND_MESSAGE):
            event = SendMessageEvent(context, event_id, date, userInfo,
                                     siteInfo, instanceDatum,
                                     supplementaryDatum)
        elif (code == CREATE_MESSAGE):
            event = CreateMessageEvent(context, event_id, date, userInfo,
                                       siteInfo, instanceDatum)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date,
                                    userInfo, instanceUserInfo, siteInfo,
                                    groupInfo, instanceDatum,
                                    supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


@implementer(IAuditEvent)
class SendNotificationEvent(BasicAuditEvent):
    """A user being send a standard notificaion.

    ``instanceDatum``
        The type of notification that is sent.

    ``supplementaryDatum``
        The ID of the notification that is sent.
    """
    def __init__(self, context, eventId, d, userInfo, siteInfo,
                 instanceDatum, supplementaryDatum):
        super(SendNotificationEvent, self).__init__(
            context, eventId, SEND_NOTIFICATION, d, userInfo, None,
            siteInfo, None, instanceDatum, supplementaryDatum, SUBSYSTEM)

    def __unicode__(self):
        m = 'Sending the notification {0}/{1} to {2} ({3}) on {4} ({5})'
        retval = m.format(self.instanceDatum, self.supplementaryDatum,
                          self.userInfo.name, self.userInfo.id,
                          self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event profile-notify-event-%s' % self.code
        notif = '<code class="notification">%s/%s</code>' % \
            (self.instanceDatum, self.supplementaryDatum)
        retval = '<span class="%s">Sent the notification %s.</span>' %\
            (cssClass, notif)
        return retval


@implementer(IAuditEvent)
class SendMessageEvent(BasicAuditEvent):
    """A message being sent to the user.

    ``instanceDatum``
        The email address being used.

    ``supplementaryDatum``
        The length of the message.
    """
    def __init__(self, context, eventId, d, userInfo, siteInfo,
                 instanceDatum, supplementaryDatum):

        super(SendMessageEvent, self).__init__(
            context, eventId, SEND_MESSAGE, d, userInfo, None, siteInfo,
            None, instanceDatum, supplementaryDatum, SUBSYSTEM)

    def __unicode__(self):
        r = 'Message of {0} characters being sent to the address <{1}> of '\
            '{2} ({3}) on {4} ({5})'
        retval = r.format(to_unicode_or_bust(self.instanceDatum),
                          to_unicode_or_bust(self.supplementaryDatum),
                          to_unicode_or_bust(self.userInfo.name),
                          to_unicode_or_bust(self.userInfo.id),
                          to_unicode_or_bust(self.siteInfo.name),
                          to_unicode_or_bust(self.siteInfo.id))
        assert type(retval) == unicode
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event profile-notify-event-%s' % self.code
        email = '<code class="email">%s</code>' % self.supplementaryDatum
        retval = '<span class="%s">Message of %s characters sent to '\
                 '%s.</span>' % (cssClass, self.instanceDatum, email)
        return retval


@implementer(IAuditEvent)
class CreateMessageEvent(BasicAuditEvent):
    """A notification being created.

    ``instanceDatum``
        The subject line of the notification.
    """
    def __init__(self, context, eventId, d, userInfo, siteInfo,
                 instanceDatum):

        super(CreateMessageEvent, self).__init__(
            context, eventId, CREATE_MESSAGE, d, userInfo, None, siteInfo,
            None, instanceDatum, None, SUBSYSTEM)

    def __unicode__(self):
        m = 'Notification "{0}" created for {1} ({2}) on {3} ({4})'
        retval = m.format(to_unicode_or_bust(self.instanceDatum),
                          to_unicode_or_bust(self.userInfo.name),
                          to_unicode_or_bust(self.userInfo.id),
                          to_unicode_or_bust(self.siteInfo.name),
                          to_unicode_or_bust(self.siteInfo.id))
        assert type(retval) == unicode
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event profile-notify-event-{0}'.format(self.code)
        r = '<span class="{0}">Notification <cite>{1}</cite> created</span>'
        retval = r.format(cssClass, self.instanceDatum)
        return retval


class Auditor(object):
    def __init__(self, siteInfo, user):
        if not siteInfo:
            m = 'No siteInfo'
            raise ValueError(m)
        self.siteInfo = siteInfo

        if not user:
            m = 'No userInfo'
            raise ValueError(m)
        if IGSUserInfo.providedBy(user):
            self.userInfo = user
        else:
            self.userInfo = IGSUserInfo(user)

        self.queries = AuditQuery()
        self.factory = AuditEventFactory()

    def info(self, code, instanceDatum='', supplementaryDatum=''):
        d = datetime.now(UTC)
        iD = to_ascii(instanceDatum)
        sD = to_ascii(supplementaryDatum)
        eventId = event_id_from_data(self.userInfo, self.userInfo,
                                     self.siteInfo, code, iD, sD)

        e = self.factory(self.userInfo.user, eventId, code, d,
                         self.userInfo, None, self.siteInfo, None,
                         instanceDatum, supplementaryDatum, SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
