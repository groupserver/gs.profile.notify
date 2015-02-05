=====================
``gs.profile.notify``
=====================
~~~~~~~~~~~~~~~~~~~~~~~~~~
Notifications to a profile
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2015-02-04
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.

..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/

Introduction
============

Notifications are small messages that are sent to the user
outside the group-email context. In this document I discuss `how
to write a notification`_ and document the `MessageSender`_ class
that sends the message.

How to Write a Notification
===========================

Or, more correctly, how Michael writes notifications.

I write notifications in three steps: `1. Write an HTML Page`_,
`2. Write a Text Page`_, and `3. Write a Notifier`_.

1. Write an HTML Page
---------------------

A `MessageSender`_ takes both a HTML and a plain-text version of
a message. However, I find it easier to start with the HTML form,
and then work on the text-version (see `2. Write a Text Page`_
below). I write the HTML form of the message as a normal
page-view.

* If the message is about the group I will make the view a
  ``GroupPage`` [#GroupPage]_, so it is in the group context
  [#GroupContext]_. Messages about group members are also placed
  in the group-context, so the permissions are correct.

* If the message is about an individual I will page the page a
  ``ProfilePage`` [#ProfilePage]_, so it is in the context of a
  user [#UserContext]_.

The view sometimes has code specific to the message, just like
other page-views often have page-specific code in them.

At the top of the page-template I set up all the arguments to the
page. Later these will be passed in as *options* (see `3. Write a
Notifier`_ below). However, for prototyping it is easier to use
hard-coded defaults if the arguments are not supplied:


.. code-block:: xml

  <html 
    tal:define="userInfo options/userInfo | view/userInfo;
      emailAddress options/emailAddress | string:placeholder@email.address;
      verifyLink options/verifyLink | string:${view/siteInfo/url}/r/verify/placeholder">

The above code is in the context of a user, so there is always a
``view/userInfo`` available for the ``userInfo`` option. In the
group-context I use the logged-in user information
(``self.loggedInUserInfo``) to fill in the user-specific
details. The two other options use place-holder strings: one
completely hard-coded, and one with some site-specific
information.

2. Write a Text Page
--------------------

The text-page is normally a cut-down version of the HTML-page. It
hangs off the same marker interfaces, and I will give the page
the same name, except with a ``.txt`` extension.

I normally make the view a subclass of the HTML view. In the
``__init__`` I change the ``request``, so the HTTP headers are
correct:

.. code-block:: python

  response = request.response
  response.setHeader(b"Content-Type", b'text/plain; charset=UTF-8')
  filename = b'verify-address-%s.txt' % self.userInfo.name
  response.setHeader(b'Content-Disposition',
                     b'inline; filename="%s"' % filename)

The page-template itself normally follows the HTML closely, but
with all styling removed and the remaining elements replaced with
``tal:block`` elements.

3. Write a Notifier
-------------------

A notifier is what is called by the UI to send the message. It
creates the HTML and text forms of the message, and sends it to
the correct people.

Initialisation:
  The notifier needs access to both the ``request`` and ``context``. 
  Both need to be passed in from the UI.

HTML Template:
  This *property* acquires the HTML view of the message. To do this it 
  calls:
  
  .. code-block:: python

      getMultiAdapter((self.context, self.request), 
                      name=self.htmlTemplateName)
  
  This is the same way that the normal publishing system acquires the 
  view for display. The view is not rendered until the ``notify`` method
  is called (see below).
  
Text Template:
  This *property* works much the same way as the HTML Template property,
  but the name of the text-view is passed in.

Notify:
  This **method** does three things.
  
  #.  Renders the HTML and text versions of the message. It does
      this by passing in any options that are needed by the
      page. For example:

      .. code-block:: python

          text = self.textTemplate(userInfo=userInfo)
          html = self.htmlTemplate(userInfo=userInfo)

  #.  Instantiating the `MessageSender`_ class.
  #.  Calling the ``send_message`` method of the
      ``MessageSender`` class.

The main difference between the different ``Notify`` classes are
different views are created (the names passed to the
named-adaptor calls are different), and the ``notify`` method
takes different arguments. These arguments are normally blindly
passed on to the two views.

The notifier requires a ``context`` and a ``request``. Because of
this it is the responsibility of the user-interfaces (normally
forms) to send the notifications. It is not the responsibility of
the low-level code that actually does the work.

``MessageSender``
=================

The ``MessageSender`` [#MessageSender]_ is used to send a
pre-written message to someone. To *initialise* the class pass in
a ``context`` and a user-info for the person who is to receive
the message.

The main method used to send a message is:
          
.. code-block:: python

    def send_message(self, subject, txtMessage, htmlMessage='', 
                     fromAddress=None, toAddresses=None)

* If only the ``subject`` and ``txtMessage`` arguments are given
  then the message will be sent to the default email addresses of
  the user that was passed in when the message sender was
  initialised.

* If the optional ``htmlMessage`` is provided then a multipart
  email message will be created, with both the text and HTML
  forms of the message set.

* The ``fromAddress`` sets who sent the message. If omitted the
  email address of the *Support* group is used [#FromAddress]_.

* Finally, the ``toAddress`` is a list of email addresses to send
  the notification to. If omitted the system will use default
  (preferred) addresses of the user that was passed in when the
  message sender was initialised [#ToAddress]_.

The ``MessageSender`` does not, ultimately, send the
message. Instead it formats the message [#MIME]_, and then calls
``NotifyUser`` [#NotifyUser]_. The ``send_message`` method of
this class sends the message on its way by calling the
``send_email`` function from the ``gs.email`` component.

Resources
=========

- Code repository: https://github.com/groupserver/gs.profile.notify
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17

..  [#GroupPage] See ``gs.group.base``
                 <https://github.com/groupserver/gs.group.base>

..  [#GroupContext] A page in the group-context will hang off the
                    ``gs.group.base.interfaces.IGSGroupMarker``
                    marker interface

..  [#ProfilePage] See ``gs.profile.base``
                   <https://github.com/groupserver/gs.profile.base>
                 
..  [#UserContext] A page in the context of a user will hang off
                    the marker interface
                    ``Products.CustomUserFolder.interfaces.ICustomUser``.

..  [#MessageSender] ``gs.profile.notify.sender.MessageSender``

..  [#FromAddress] The system will fail an assertion if it cannot
                   find a user for the supplied ``fromAddress``.

..  [#ToAddress] The system will fail an assertion if a
                 ``toAddress`` is used that does not belong to
                 the user. The address may be *unverified*, but
                 it must belong to the user.

..  [#MIME] `The core Python email module
            <http://docs.python.org/library/email>`_ is used to
            format the message using MIME. It is used create one
            string that contains the basic header, text, and HTML
            portions of the message.

..  [#NotifyUser] ``gs.profile.notify.notifyuser.NotifyUser``
