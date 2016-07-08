# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2016 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals, print_function
from email.MIMEMultipart import MIMEMultipart
from mock import (MagicMock, patch, PropertyMock)
from unittest import TestCase
from gs.profile.notify.sender import MessageSender


class TestMessageSender(TestCase):

    def test_to_addresses(self):
        ms = MessageSender(MagicMock(), MagicMock())
        e = ['person@example.com', ]
        r = ms.to_addresses(e)

        self.assertEqual(e, r)

    @patch.object(MessageSender, 'emailUser', new_callable=PropertyMock)
    def test_to_addresses_none(self, m_eU):
        'Test that we get the default To address'
        e = ['person@example.com', ]
        m_eU().get_delivery_addresses.return_value = e
        ms = MessageSender(MagicMock(), MagicMock())
        r = ms.to_addresses(None)

        self.assertEqual(e, r)

    def test_from_address(self):
        'Test we get the From address when asked'
        ms = MessageSender(MagicMock(), MagicMock())
        e = 'support@example.com'
        r = ms.from_address(e)

        self.assertEqual(e, r)

    @patch.object(MessageSender, 'siteInfo', new_callable=PropertyMock)
    def test_from_address_none(self, m_sI):
        'Test that we get the default From address'
        e = 'support@example.com'
        m_sI().get_support_email.return_value = e
        ms = MessageSender(MagicMock(), MagicMock())
        r = ms.from_address(None)

        self.assertEqual(e, r)

    def test_get_addr_line(self):
        ms = MessageSender(MagicMock(), MagicMock())
        r = ms.get_addr_line('Example support', 'support@example.com')
        self.assertEqual('Example support <support@example.com>', r)

    def test_get_addr_line_unicode(self):
        ms = MessageSender(MagicMock(), MagicMock())
        r = ms.get_addr_line('Example support\u203d', 'support@example.com')
        self.assertEqual('=?utf-8?q?Example_support=E2=80=BD?= <support@example.com>', r)

    def test_get_addr_line_no_name(self):
        ms = MessageSender(MagicMock(), MagicMock())
        r = ms.get_addr_line('', 'support@example.com')
        self.assertEqual('support@example.com', r)

    @patch.object(MessageSender, 'siteInfo', new_callable=PropertyMock)
    def test_from_header_from_address_none(self, m_sI):
        m_sI().name = 'Example'
        m_sI().get_support_email.return_value = 'support@example.com'
        context = MagicMock()
        ms = MessageSender(context, MagicMock())
        r = ms.from_header_from_address(None)

        self.assertEqual('Example Support <support@example.com>', r)

    def test_from_header_from_address_not_a_user(self):
        context = MagicMock()
        context.acl_users.get_userByEmail.return_value = None
        ms = MessageSender(context, MagicMock())

        with self.assertRaises(ValueError):
            ms.from_header_from_address('group@example.com')

    @patch('gs.profile.notify.sender.IGSUserInfo')
    def test_from_header_from_address_user(self, m_IGSUI):
        context = MagicMock()
        m_IGSUI().name = 'Example person'
        ms = MessageSender(context, MagicMock())
        r = ms.from_header_from_address('person@example.com')

        self.assertEqual('Example person <person@example.com>', r)

    @patch.object(MessageSender, 'to_addresses')
    def test_to_header_from_addresses_issues(self, m_t_a):
        'Test we raise a ValueError if we lack and address to send to'
        m_t_a.return_value = None
        ms = MessageSender(MagicMock(), MagicMock())
        with self.assertRaises(ValueError):
            ms.to_header_from_addresses(None)

    @patch.object(MessageSender, 'to_addresses')
    def test_to_header_from_addresses_none(self, m_t_a):
        'Ensure we used the default address if we are given no address'
        m_t_a.return_value = ['person@example.com', ]
        toUserInfo = MagicMock()
        toUserInfo.name = 'Example Person'
        ms = MessageSender(MagicMock(), toUserInfo)
        r = ms.to_header_from_addresses(None)

        self.assertEqual('Example Person <person@example.com>', r)

    @patch.object(MessageSender, 'to_addresses')
    def test_to_header_from_addresses_none_multiple(self, m_t_a):
        'Ensure we handle multiple to-addresses correctly if they are the default'
        m_t_a.return_value = ['person@example.com', 'other@example.com', ]
        toUserInfo = MagicMock()
        toUserInfo.name = 'Example Person'
        ms = MessageSender(MagicMock(), toUserInfo)
        r = ms.to_header_from_addresses(None)

        expected = 'Example Person <person@example.com>, Example Person <other@example.com>'
        self.assertEqual(expected, r)

    def test_to_header_from_addresses_multiple(self):
        'Ensure we handle multiple to-addresses correctly'
        addr = ['person@example.com', 'other@example.com', ]
        toUserInfo = MagicMock()
        toUserInfo.name = 'Example Person'
        ms = MessageSender(MagicMock(), toUserInfo)
        r = ms.to_header_from_addresses(addr)

        expected = 'Example Person <person@example.com>, Example Person <other@example.com>'
        self.assertEqual(expected, r)

    def test_to_header_from_addresses_single(self):
        'Ensure we handle a single to-addresses correctly'
        addr = ['person@example.com', ]
        toUserInfo = MagicMock()
        toUserInfo.name = 'Example Person'
        ms = MessageSender(MagicMock(), toUserInfo)
        r = ms.to_header_from_addresses(addr)

        self.assertEqual('Example Person <person@example.com>', r)

    @patch.object(MessageSender, 'from_header_from_address')
    @patch.object(MessageSender, 'to_header_from_addresses')
    def test_set_headers(self, m_to, m_from):
        m_to.return_value = 'person@example.com'
        m_from.return_value = 'support@example.com'
        container = MIMEMultipart('alternative')
        ms = MessageSender(MagicMock(), MagicMock())
        subj = 'Ethel the Frog'
        ms.set_headers(container, subj, 'mockFrom', 'mockTo')

        self.assertEqual(subj, container['Subject'])
        m_from.assert_called_once_with('mockFrom')
        self.assertEqual(m_from(), container['From'])
        m_to.assert_called_once_with('mockTo')
        self.assertEqual(m_to(), container['To'])
        # Only test the presence of a date, because race-conditions with dates
        self.assertIn('Date', container)

    @patch.object(MessageSender, 'siteInfo', new_callable=PropertyMock)
    @patch.object(MessageSender, 'emailUser', new_callable=PropertyMock)
    @patch('gs.profile.notify.sender.IGSUserInfo')
    @patch('gs.profile.notify.sender.Auditor')
    def test_create_message_no_html(self, m_A, m_IGUI, m_eU, m_sI):
        m_sI().name = 'Example'
        m_sI().get_support_email.return_value = 'support@example.com'
        m_eU().get_delivery_addresses.return_value = ['person@example.com', ]
        toUserInfo = MagicMock()
        toUserInfo.name = 'Example Person'
        ms = MessageSender(MagicMock(), toUserInfo)
        r = ms.create_message('Ethel the Frog',
                              'Tonight on Ethel the Frog we look at violence\u2026',
                              None, None, None)
        self.assertNotIn('html', r)
        self.assertIn('text/plain', r)
        self.assertIn('Subject: Ethel the Frog', r)
        self.assertIn('To: Example Person <person@example.com>', r)

    @patch.object(MessageSender, 'siteInfo', new_callable=PropertyMock)
    @patch.object(MessageSender, 'emailUser', new_callable=PropertyMock)
    @patch('gs.profile.notify.sender.IGSUserInfo')
    @patch('gs.profile.notify.sender.Auditor')
    def test_create_message_html(self, m_A, m_IGUI, m_eU, m_sI):
        m_sI().name = 'Example'
        m_sI().get_support_email.return_value = 'support@example.com'
        m_eU().get_delivery_addresses.return_value = ['person@example.com', ]
        toUserInfo = MagicMock()
        toUserInfo.name = 'Example Person'
        ms = MessageSender(MagicMock(), toUserInfo)
        r = ms.create_message('Ethel the Frog',
                              'Tonight on Ethel the Frog we look at violence\u2026',
                              '<p>Tonight on Ethel the Frog we look at violence&#8230</p>',
                              None, None)
        self.assertIn('text/html', r)
        self.assertIn('text/plain', r)
        self.assertIn('Subject: Ethel the Frog', r)
        self.assertIn('To: Example Person <person@example.com>', r)

    @patch.object(MessageSender, 'siteInfo', new_callable=PropertyMock)
    @patch.object(MessageSender, 'emailUser', new_callable=PropertyMock)
    @patch('gs.profile.notify.sender.IGSUserInfo')
    @patch('gs.profile.notify.sender.Auditor')
    @patch('gs.profile.notify.sender.NotifyUser')
    def test_send_message(self, m_NU, m_A, m_IGUI, m_eU, m_sI):
        m_sI().name = 'Example'
        m_sI().get_support_email.return_value = 'support@example.com'
        m_eU().get_delivery_addresses.return_value = ['person@example.com', ]
        toUserInfo = MagicMock()
        toUserInfo.name = m_IGUI().name = 'Example Person'
        ms = MessageSender(MagicMock(), toUserInfo)
        ms.send_message('Ethel the Frog',
                        'Tonight on Ethel the Frog we look at violence\u2026',
                        '<p>Tonight on Ethel the Frog we look at violence&#8230</p>',
                        'support@example.com',
                        ['person0@example.com', 'person1@example.com', ])
        self.assertEqual(2, m_NU().send_message.call_count)
