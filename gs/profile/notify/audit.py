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
from pytz import UTC
from datetime import datetime
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, \
  AuditQuery, event_id_from_data

SUBSYSTEM = 'gs.profile.notify'
import logging
log = logging.getLogger(SUBSYSTEM)

UNKNOWN = '0'
SEND_NOTIFICATION = '1'
SEND_MESSAGE = '2'
CREATE_MESSAGE = '3'


class AuditEventFactory(object):
    implements(IFactory)

    title = u'User Profile Notification Audit-Event Factory'
    description = u'Creates a GroupServer audit event for notifications'

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
              userInfo, instanceUserInfo, siteInfo, groupInfo,
              instanceDatum, supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


class SendNotificationEvent(BasicAuditEvent):
    """A user being send a standard notificaion.

    ``instanceDatum``
        The type of notification that is sent.

    ``supplementaryDatum``
        The ID of the notification that is sent.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, siteInfo, instanceDatum,
                    supplementaryDatum):
        BasicAuditEvent.__init__(self, context, id, SEND_NOTIFICATION,
                                    d, userInfo, None, siteInfo, None,
                                    instanceDatum, supplementaryDatum,
                                    SUBSYSTEM)

    def __unicode__(self):
        m = u'Sending the notification {0}/{1} to {2} ({3}) on {4} ({5})'
        retval = m.format(self.instanceDatum, self.supplementaryDatum,
                          self.userInfo.name, self.userInfo.id,
                          self.siteInfo.name, self.siteInfo.id)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event profile-notify-event-%s' % self.code
        notif = u'<code class="notification">%s/%s</code>' % \
            (self.instanceDatum, self.supplementaryDatum)
        retval = u'<span class="%s">Sent the notification %s.</span>' %\
            (cssClass, notif)
        return retval


class SendMessageEvent(BasicAuditEvent):
    """A message being sent to the user.

    ``instanceDatum``
        The email address being used.

    ``supplementaryDatum``
        The length of the message.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, siteInfo, instanceDatum,
                    supplementaryDatum):

        BasicAuditEvent.__init__(self, context, id, SEND_MESSAGE, d,
            userInfo, None, siteInfo, None, instanceDatum,
            supplementaryDatum, SUBSYSTEM)

    def __unicode__(self):
        r = u'Message of {0} characters being sent to the address <{1}> of '\
            u'{2} ({3}) on {4} ({5})'
        retval = r.format(self.instanceDatum, self.supplementaryDatum,
                            self.userInfo.name, self.userInfo.id,
                            self.siteInfo.name, self.siteInfo.id)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event profile-notify-event-%s' % self.code
        email = u'<code class="email">%s</code>' % self.supplementaryDatum
        retval = u'<span class="%s">Message of %s characters sent to '\
            u'%s.</span>' % (cssClass, self.instanceDatum, email)
        return retval


class CreateMessageEvent(BasicAuditEvent):
    """A notification being created.

    ``instanceDatum``
        The subject line of the notification.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, siteInfo, instanceDatum):

        BasicAuditEvent.__init__(self, context, id, CREATE_MESSAGE, d,
            userInfo, None, siteInfo, None, instanceDatum, None, SUBSYSTEM)

    def __unicode__(self):
        m = u'Notification "{0}" created for {1} ({2}) on {3} ({4})'
        retval = m.format(self.instanceDatum,
                            self.userInfo.name, self.userInfo.id,
                            self.siteInfo.name, self.siteInfo.id)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event profile-notify-event-{0}'.format(self.code)
        r = u'<span class="{0}">Notification <cite>{1}</cite> created</span>'
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
        eventId = event_id_from_data(self.userInfo, self.userInfo,
            self.siteInfo, code, instanceDatum, supplementaryDatum)

        e = self.factory(self.userInfo.user, eventId, code, d,
                self.userInfo, None, self.siteInfo, None,
                instanceDatum, supplementaryDatum, SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
