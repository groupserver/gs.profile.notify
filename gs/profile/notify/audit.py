# coding=utf-8
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

    def __str__(self):
        retval = u'Sending the notification %s/%s to %s (%s) on %s (%s)' %\
          (self.instanceDatum, self.supplementaryDatum,
          self.userInfo.name, self.userInfo.id,
          self.siteInfo.name, self.siteInfo.id)
        return retval.encode('ascii', 'ignore')

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

    def __str__(self):
        retval = u'Message of %s characters being sent to the address '\
          u'<%s> of %s (%s) on %s (%s)' %\
          (self.instanceDatum, self.supplementaryDatum,
            self.userInfo.name, self.userInfo.id,
            self.siteInfo.name, self.siteInfo.id)
        return retval.encode('ascii', 'ignore')

    @property
    def xhtml(self):
        cssClass = u'audit-event profile-notify-event-%s' % self.code
        email = u'<code class="email">%s</code>' % self.supplementaryDatum
        retval = u'<span class="%s">Message of %s characters sent to '\
            u'%s.</span>' % (cssClass, self.instanceDatum, email)
        return retval


class Auditor(object):
    def __init__(self, siteInfo, user):
        assert siteInfo, 'siteInfo is %s' % siteInfo
        assert user, 'user is %s' % user
        self.siteInfo = siteInfo
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
