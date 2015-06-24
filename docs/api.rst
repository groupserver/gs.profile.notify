============================
:mod:`gs.profile.notify` API
============================

.. currentmodule:: gs.profile.notify

The :class:`MessageSender` class is the main symbol provided by
the :mod:`gs.profile.notify` product.

.. class:: MessageSender(context, userInfo)

   :param context: The context of the message.
   :param userInfo: The person to send the message to.
   :type userInfo: :class:`Products.CustomUserFolder.interfaces.IGSUserInfo`

   The :class:`MessageSender` is used to send a pre-written
   message to someone. To *initialise* the class pass in a
   ``context`` and a user-info for the person who is to receive
   the message.

   .. function:: send_message(self, subject, txtMessage, htmlMessage='',
                              fromAddress=None, toAddresses=None)

      :param str subject: The subject (the :mailheader:`Subject`
                          header) of the message.
      :param str txtMessage: The plain-text
                             (:mimetype:`text/plain`) version of
                             the message.
      :param str htmlMessage: The HTML version
                              (:mimetype:`text/html`) of the
                              message.
      :param str fromAddress: The address the email is sent
                              *from* (the :mailheader:`From`
                              header).
      :param toAddress: The addresses the email is sent *to*
                        (the :mailheader:`Tp` header).
      :type toAddress: list or None

      * If only the ``subject`` and ``txtMessage`` arguments are
        given then the message will be sent to the default email
        addresses of the user that was passed in when the message
        sender was initialised.
      * If the optional ``htmlMessage`` is provided then a
        :mimetype:`multipart/alternative` email message will be
        created (:rfc:`2046#section-5.1.4`), with both the text
        and HTML forms of the message set.
      * The ``fromAddress`` sets who sent the message. If omitted
        the email address of the *Support* group is used
        [#FromAddress]_.
      * Finally, the ``toAddress`` is a list of email addresses
        to send the notification to. If omitted the system will
        use default (preferred) addresses of the user that was
        passed in when the message sender was initialised
        [#ToAddress]_.

The :class:`MessageSender` does not, ultimately, send the
message. Instead it formats the message [#MIME]_, and then calls
:class:`gs.profile.notify.notifyuser.NotifyUser`. The
:func:`gs.profile.notify.notifyuser.NotifyUser.send_message`
method of this class sends the message on its way by calling the
:func:`gs.email.send_email` function.

..  [#FromAddress] The system will fail an assertion if it cannot
                   find a user for the supplied ``fromAddress``.

..  [#ToAddress] The system will fail an assertion if a
                 ``toAddress`` is used that does not belong to
                 the user. The address may be *unverified*, but
                 it must belong to the user.

..  [#MIME] The core Python :mod:`email` module is used to format
            the message using MIME.
