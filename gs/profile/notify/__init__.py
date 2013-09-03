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
#lint:disable
from notifyuser import NotifyUser
from sender import MessageSender
#lint:enable

from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class
m_security = ModuleSecurityInfo('gs.profile.notify.notifyuser')
m_security.declarePublic('NotifyUser')
allow_class(NotifyUser)
