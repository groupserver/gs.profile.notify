===========================
How to Write a Notification
===========================

.. currentmodule:: gs.profile.notify

Or, more correctly, how Michael_ writes notifications.

I write notifications in three steps: `1. Write an HTML Page`_,
`2. Write a Text Page`_, and `3. Write a Notifier`_.

1. Write an HTML Page
---------------------

A :class:`MessageSender` takes both a HTML and a plain-text
version of a message. However, I find it easier to start with the
HTML form, and then work on the text-version (see `2. Write a
Text Page`_ below). I write the HTML form of the message as a
normal page-view.

If the message is **about a group,** or a group member, I will
make the view a subclass of the
:class:`gs.content.email.base.GroupEmail` class [#EmailBase]_, so
it is in the group context [#GroupContext]_.

    .. code-block:: python

       class InvitationMessage(GroupEmail):

           def __init__(self, context, request):
               super(InvitationMessage, self).__init__(context, request)

Messages about group members are placed in the group-context so
the permissions are correct.

    .. code-block:: xml

       <browser:page
         name="invitationmessage.html"
         for="gs.group.base.interfaces.IGSGroupMarker"
         class=".notifymessages.InvitationMessage"
         template="browser/templates/new-invitationmessage.pt"
         permission="zope2.View" />

If the message is *just* **about an individual,** removed from
the context of the group, I will make the page a subclass of the
:class:`gs.content.email.base.SiteEmail` class [#EmailBase]_.

     .. code-block:: python

        from gs.content.email.base import SiteEmail, TextMixin

        class ProfileStatus(SiteEmail):
            'The profile-status notification'

The page is rendered in the context of a user it is in the
context of a user [#UserContext]_.

     .. code-block:: xml

        <browser:page
          name="gs-profile-status.html"
          for="Products.CustomUserFolder.interfaces.ICustomUser"
          class=".notification.ProfileStatus"
          template="browser/templates/notification-html.pt"
          permission="zope2.ManageProperties" />

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

I normally make the view a subclass of the HTML view, and make
use of the :class:`from gs.content.email.base.TextMixin` class.

.. code-block:: python

   class SomeNotificationText(SomeNotificationHTML, TextMixin):

       def __init__(self, context, request):
           super(SomeNotificationText, self).__init__(context, request)
           filename = 'some-notification-{0}.txt'.format(self.groupInfo.id)
           self.set_header(filename)

       def format_message_no_indent(self, m):
           tw = TextWrapper()
           retval = tw.fill(m)
           return retval

The page-template itself normally follows the HTML closely, but
with all styling removed and the remaining elements replaced with
``<tal:block />`` elements.

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

  #.  Instantiating the :class:`MessageSender` class.
  #.  Calling the :func:`MessageSender.send_message` method.

The main difference between the different Notify classes are
different views are created (the names passed to the
named-adaptor calls are different), and the ``notify`` method
takes different arguments. These arguments are normally blindly
passed on to the two views.

The notifier requires a ``context`` and a ``request``. Because of
this it is the responsibility of the user-interfaces (normally
forms) to send the notifications. It is not the responsibility of
the low-level code that actually does the work.

.. _Michael: http://groupserver.org/p/mpj17

..  [#EmailBase] See :mod:`gs.content.email.base`
                 <https://github.com/groupserver/gs.content.email.base>

..  [#GroupContext] A page in the group-context will hang off the
                    :class:`gs.group.base.interfaces.IGSGroupMarker`
                    marker interface

..  [#ProfilePage] See ``gs.profile.base``
                   <https://github.com/groupserver/gs.profile.base>

..  [#UserContext] A page in the context of a user will hang off
                    the marker interface
                    ``Products.CustomUserFolder.interfaces.ICustomUser``.
