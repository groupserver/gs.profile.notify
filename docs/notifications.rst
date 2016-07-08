=========================
GroupServer Notifications
=========================

:Authors: Alice Murphy; Michael JasonSmith
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Organization: `GroupServer.org`_
:Date: 2015-04-27
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.

..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/

.. contents:: `Table of contents`
   :depth: 2

Notifications are small messages that are sent to the user
outside the group-email context. They include messages such as
the `invitation`_ to join a group, and the `group welcome`_
email. In this document we describe the various notifications
sent by GroupServer. We summarise who they are sent to, and the
code-path that is followed to send the notification.

Currently the notifications are being transitioned to their third
version. These `file-system-side notifications`_ are are more
flexible than the old `notification templates`_. The
notifications in different sub-systems will be converted to
file-system side notifications when each module is reviewed in
the normal process of software maintenance and refactoring.

File-System-Side Notifications
==============================

As we rebuild each subsystem, we move its notifications to the
file system, from the ZMI. The file-system-side notifications
work like Web pages. The notification system renders two pages —
an HTML page and a plain-text version of the same message — and
places them in an email message. All of the new fine-system-side
notifications use :class:`gs.profile.notify.sender.MessageSender`
to send the message.

Cannot Post
-----------

Sent to a person with a profile when they attempt to post to a group, 
but disallowed. The content of the message comes from the viewlets that
make up the ``gs.group.type.*`` eggs. For people people without a 
profile see `unknown email address`_.

:Sent to: The a person with a profile that cannot post to the group.
:URL: *Group Page* ``/cannot-post.html``
:via:
  | ``Products.XWFMailingListManager.XWFMailingList.checkMail``
  | ``gs.group.member.canpost.notifier.Notifier``
  | ``gs.group.member.canpost.notifier.CannotPostMessageSender``
  | ``gs.profile.notify.notifyuser.NotifyUser``

Invitation
----------

An invitation is a message from an administrator asking someone
to join the group. It is also used to present the administrator
with a *preview* of the invitation.

:Sent to: Someone who has been invited to join a group by the
          administrator.
:URL: *Group page* ``/invitationmessage.html``
:via: Clicking *Invite*

  | ``gs.group.member.invite.base.invite.InviteEditProfileForm``
  | ``gs.group.member.invite.base.processor.InviteProcessor``
  | ``gs.group.member.invite.base.inviter.Inviter``
  | ``gs.group.member.invite.base.notify.InvitationNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`
  |
  | Invite site member: ``gs.group.member.invite.invitesitemembers.GSInviteSiteMembersForm``
  | ``gs.group.member.invite.json.api.InviteUserAPI``
  | ``gs.group.member.invite.base.processor.InviteProcessor``
  | ...
  |
  | Invite in bulk: ``gs.group.member.invite.csv.ui.CSVUploadUI``
  | ``gs.group.member.invite.json.api.InviteUserAPI``
  | ``gs.group.member.invite.base.processor.InviteProcessor``
  | ...
  |
  | Resend: ``gs.group.member.invite.resend.reinvite.ResendInvitationForm``
  | ``gs.group.member.invite.base.processor.InviteProcessor``
  | ...

Group Welcome
-------------

The *Group Welcome* notification is sent to a new member when he
or she joins a group. However, there are many ways of becoming a
member, and some still use the old code, rather than this shiny
method.

Site administrators receive the `New Member`_ notification.

:Sent to: A new member of a group.
:URL: *Group page* ``/new-member-msg.html``
:via: A *logged in member* clicks ``Join`` in a Public group.

  | ``gs.group.join.join.JoinForm``
  | ``gs.group.join.notify.NotifyNewMember``
  | :class:`gs.profile.notify.sender.MessageSender`
  |
  | A new **invited** member accepts an invitation to join a group
  | ``gs.profile.invite.initalresponse``
  |
  | An existing **invited** member accepts an invitation to join a group.
  | ``gs.profile.invite.invitationsrespond``
  |
  | A new member joins a group during **registration** 
  | ``gs.profile.signup.base.changeprofile.ChangeProfileForm``  
  | *or* ``gs.profile.signup.base.verifywait.VerifyWaitForm``

Group Started
-------------

Information about the group that has just been started

:Sent to: Every site administrator.
:URL: *Group page* ``/gs-group-start.html``
:via: A *site administrator* clicks ``Start``

  | ``gs.group.start.startgroup.StartGroupForm``
  | ``gs.group.start.notify.StartNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

New Member
----------

Sent to the group administrators when a new member joins the
group. It is the flip-side of the `group welcome`_ notification.

:Sent to: The group administrators, or the site administrators if
          there are no group administrators.
:URL: *Group page* ``/new-member-admin-msg.html``
:via: A *logged in member* clicks ``Join`` in a Public group.

  | ``gs.group.join.join.JoinForm``
  | ``gs.group.join.notify.NotifyAdmin``
  | :class:`gs.profile.notify.sender.MessageSender`
  |
  | A new **invited** member accepts an invitation to join a group
  | ``gs.profile.invite.initalresponse``
  |
  | An existing **invited** member accepts an invitation to join a 
    group
  | ``gs.profile.invite.invitationsrespond``
  |
  | An administrator accepts the *request* to join the group. #3469
  | ``gs.group.member.request.request.respond.Respond``
  |
  | A new member joins a group during **registration**
  | ``gs.profile.signup.base.changeprofile.ChangeProfileForm`` 
  | *or* ``gs.profile.signup.base.verifywait.VerifyWaitForm``

Request Membership
------------------

This message is sent when someone requests to become a member of a
Private group. It is the opposite of a `invitation`_. It should not
be confused with `Request Contact`_.

:Sent to: The administrator of the group.
:URL: *Group page* ``/request_message.html``
:via: The request membership form
  | ``gs.group.member.request.request.RequestForm``
  | :class:`gs.profile.notify.sender.MessageSender`

Request Contact
---------------

This notification is sent when a member reaches out to
another. It allows the email address of everyone to be kept
secret until they chose to disclose it. It is unusual because the
:mailheader:`From` and :mailheader:`Reply-to` addresses are different.

:Sent to: The person being contacted.
:URL: *Profile page* ``/request_contact.html``
:via: The request contact form
  | ``gs.profile.contact.request.RequestContact``
  | ``gs.profile.contact.notify.RequestNotifier``
  | ``gs.profile.contact.notify.AlternateReplyMessageSender``
  | :class:`gs.profile.notify.sender.MessageSender`
  
Reset password
--------------

A link to reset a password, sent to an email address that is
submitted via the *Reset Password* page, when the email address
is recognised as belonging to a user.

:Sent to: The person that requested the password reset.
:URL: ``gs-profile-password-reset-message.html`` in the context of a user.
:via:
   | ``gs,profile.password.request.RequestPasswordResetForm``
   | ``gs,profile.password.notifier.ResetNotifier``
   | :class:`gs.profile.notify.sender.MessageSender`

Topic digest
------------

The topic digest contains a summary of the topics that were
discussed recently in the group. A "cron-job" is used to
regularly send out the digests, using the ``senddigest``
command. The digest system consists of two notifications: `the
daily digest`_, and `the weekly digest`_. In addition there are
two commands: the `digest on command`_, and the `digest off
command`_.

The daily digest
~~~~~~~~~~~~~~~~

The daily digest of topics topic digest is sent every day when
there are posts. The digest

:Sent to: All group members who have elected to receive posts in
          digest form.
:URL: *Group Page* ``gs-group-messages-topic-digest-daily.html``
:via:
  | ``gs.group.messages.topic.digest.send.script.main``
  | ``gs.group.messages.topic.digest.send.script.send_digest``
  |  *Site page* ``gs-group-messages-topic-digest-send.html``
  | ``gs.group.messages.topic.digest.base.sendDigests.SendDigests``
  | [``gs.group.messages.topic.digest.daily.notifier.DailyDigestNotifier``]
  | ``gs.group.messages.topic.digest.base.notifier.DigestNotifier.notify``
  | :func:`gs.email.send_email`

The weekly digest
~~~~~~~~~~~~~~~~~

The weekly digest is sent once a week, on the weekly-anniversary
of the last post, if there have been no posts that week.

:Sent to: All group members who have elected to receive posts in
          digest form.
:URL: *Group Page* ``gs-group-messages-topic-digest-weekly.html``
:via:
  | ``gs.group.messages.senddigest.script.main``
  | ``gs.group.messages.senddigest.script.send_digest``
  |  *Site page* ``gs-group-messages-topic-digest-send.html``
  | ``gs.group.messages.topic.digest.base.sendDigests.SendDigests``
  | [``gs.group.messages.topic.digest.weekly.notifier.WeeklyDigestNotifier``]
  | ``gs.group.messages.topic.digest.base.notifier.DigestNotifier.notify``
  | ``gs.email.send_email``

Digest on command
~~~~~~~~~~~~~~~~~

There is an email-command to turn the digest on. It is triggered
when a group member sends an email to the group with the subject
``digest on`` (case insensitive).

:Sent to: The person that asked for the digest to be turned on
:URL: ``gs-group-member-email-settings-digest-on.html`` in the
      context of a group.
:via:
   | ``gs.group.member.email.settings.listcommand.DigestCommand``
   | ``gs.group.member.email.settings.notifier.DigestOnNotifier``
   | :class:`gs.profile.notify.sender.MessageSender`

Digest off command
~~~~~~~~~~~~~~~~~~

There is an email-command to turn the digest on. It is triggered
when a group member sends an email to the group with the subject
``digest on`` (case insensitive).

:Sent to: The person that asked for the digest to be turned on
:URL: ``gs-group-member-email-settings-digest-off.html`` in the
      context of a group.
:via:
   | ``gs.group.member.email.settings.listcommand.DigestCommand``
   | ``gs.group.member.email.settings.notifier.DigestOffNotifier``
   | :class:`gs.profile.notify.sender.MessageSender`

Unknown Email Address
---------------------

A post is received by the mailing list from an unregistered email
address. It is the equivalent of the `cannot post`_ notification for
anonymous people.

:Sent to: The unrecognised email address, which sent the original message.
:URL: *Group Page* ``/unknown-email.html``
:via:
  | ``Products.XWFMailingListManager.XWFMailingList.processMail``
  | ``Products.XWFMailingListManager.XWFMailingList.mail_reply``
  | ``gs.group.member.canpost.unknownemail.Notifier``
  |
  | ``Products.XWFMailingListManager.XWFMailingList.requestMail``
  | ``Products.XWFMailingListManager.XWFMailingList.mail_reply``
  | ``gs.group.member.canpost.unknownemail.Notifier``
  | 
  | ``Products.XWFMailingListManager.XWFMailingList.processModeration``
  | ``Products.XWFMailingListManager.XWFMailingList.mail_reply``
  | ``gs.group.member.canpost.unknownemail.Notifier``

Verify Email Address
--------------------

Email addresses must be verified. The verification message is sent from
everywhere that email addresses can be added. It turns out that there are
*many* places that an email address can be added. The method
``gs.profile.email.verify.emailverificationuser.EmailVerificationUser.send_verification``
sends the verification message for all higher-level code.

:Sent to: The person who has the new address.
:URL: *Profile page* ``/verification-mesg.html``
:via: Anywhere that lets the user add an email address

  | Registering as a new user (or requesting membership as a new user)
  | ``gs.profile.signup.base.request_registration.RequestRegistrationForm``
  | ``gs.profile.email.verify.emailverificationuser.EmailVerificationUser``
  | ``gs.profile.email.verify.notify.Notifier``
  | :class:`gs.profile.notify.sender.MessageSender`
  |
  | Adding a new email address, or sending another verification message
    during registration
  | ``gs.profile.signup.base.verifywait.VerifyWaitForm``
  |
  | Adding a new email address
  | ``gs.profile.email.settings.settings.ChangeEmailSettingsForm``

Bounce
------

When GroupServer gets an XVERP return it logs a bounce. If the
group member has another email address then the user is told of
the bounce on the extra address.

:Sent to: The person who has the bouncing address
:URL: *Group page* ``/gs-group-member-bounce-bouncing.html``
:via: The *Handle bounce* page

  | ``gs.group.member.bounce.handlebounce.HandleBounce``
  | ``gs.group.member.bounce.notifier.UserBounceNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

Disabled
--------

When an address continually bounces then the address is disabled.

Disabled (user)
~~~~~~~~~~~~~~~

The user is told of that an address is disabled if he or she has
an extra address.

:Sent to: The person who has the bouncing address
:URL: *Group page* ``/gs-group-member-bounce-disabled.html``
:via: The *Handle bounce* page

  | ``gs.group.member.bounce.handlebounce.HandleBounce``
  | ``gs.group.member.bounce.notifier.UserDisabledNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

Disabled (administrator)
~~~~~~~~~~~~~~~~~~~~~~~~

The administrator is told when a member has his or her email
address disabled because of bouncing.

:Sent to: The administrators of the group that sent the post that
          bounced back.
:URL: *Group page* ``/gs-group-member-bounce-disabled-admin.html``
:via: The *Handle bounce* page

  | ``gs.group.member.bounce.handlebounce.HandleBounce``
  | ``gs.group.member.bounce.notifier.AdminDisabledNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

Leave
-----

Like joining, the member and the administrators are told that
someone has left a group. A person can leave in two ways: using
the Web or sending an email with the subject ``unsubscribe``
(case insensitive) to the group.

Leave (past member)
~~~~~~~~~~~~~~~~~~~

:Sent to: The person who has just left a group
:URL: *Group page* ``/gs-group-member-leave-notification.html``
:via: The *Leave* page

  | ``gs.group.member.leave.base.leave.LeaveForm``
  | :func:`gs.group.member.leave.base.leave_group`
  | ``gs.group.member.leave.base.notifier.LeaveNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

:via: The *Unsubscribe* command

  | ``gs.group.member.leave.command.LeaveCommand``
  | :func:`gs.group.member.leave.base.leave_group`
  | ``gs.group.member.leave.base.notifier.LeaveNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

Leave (administrator)
~~~~~~~~~~~~~~~~~~~~~

:Sent to: The administrators of a group from which a person has
          just left.
:URL: *Group page* ``/gs-group-member-leave-left.html``
:via: The *Leave* page

  | ``gs.group.member.leave.base.leave.LeaveForm``
  | :func:`gs.group.member.leave.base.leave_group`
  | ``gs.group.member.leave.base.notifier.LeftNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

:via: The *Unsubscribe* command

  | ``gs.group.member.leave.command.LeaveCommand``
  | ``gs.group.member.leave.base.notifier.LeftNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

Not a member
~~~~~~~~~~~~

If someone tries to leave, but the email address in the ``From``
header does not match then a special *Not a Member* email is sent.

:Sent to: The person who has asked to leave a group
:URL: *Groups* ``/gs-group-member-leave-not-a-member.html``
      (**Note** not the *group* page.)
:via: The *Unsubscribe* command

  | ``gs.group.member.leave.command.LeaveCommand``
  | ``gs.group.member.leave.command.notifiernonmember.NotMemberNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

Profile status
--------------

The monthly profile-status notification is sent out monthly to
everyone.

:Sent to: Every person that is in at least one group in the
          GroupServer install.
:URL: *Site page* ``/gs-profile-status.html``
:via:
  | ``gs.profile.status.send.script.main``
  | ``gs.group.messages.topic.digest.send.script.send_status``
  |  *Site page* ``/gs-profile-status.html``
  | ``gs.profile.status.base.hook.SendNotification``
  | ``gs.profile.status.base.notifier.StatusNotifier``
  | :class:`gs.profile.notify.sender.MessageSender`

Notification Templates
======================

These are the old notifications. They are DTML templates: this is the
folder in which ``Products.CustomUserFolder.Customuser.send_notification``
looks to find the notifications passed to it by ID.

Moderation
----------

Moderation is a world unto its own, and is badly need of a rewrite
[#Moderation]_.

``mail_moderated_user``
~~~~~~~~~~~~~~~~~~~~~~~

A message to the group is received from a moderated member.

**Sent to**
  | The moderated member.

**via**
  | ``Products.XWFMailingListManager.XWFMailingList.processMail``
  | ``Products.XWFMailingListManager.XWFMailingList.processModeration``
  | ``Products.CustomUserFolder.CustomUser.send_notification``

``mail_moderator``
~~~~~~~~~~~~~~~~~~

A message to the group is received from a moderated member.

**Sent to**
  | The moderators.

**via**
  | ``Products.XWFMailingListManager.XWFMailingList.processMail``
  | ``Products.XWFMailingListManager.XWFMailingList.processModeration``
  | ``Products.CustomUserFolder.CustomUser.send_notification``

..  [#Moderation] *Ticket 249: Rebuild Moderation* summarises the
    problems with moderation, and how to fix it
    <https://projects.iopen.net/groupserver/ticket/249>
  
..  _GroupServer.Org: http://groupserver.org/
..  _OnlineGroups.Net: http://onlinegroups.net/

..  LocalWords:  refactoring
