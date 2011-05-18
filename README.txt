Introduction
============

Notifications are small messages that are sent to the user outside
the group-email context. There are two classes for sending messages:
the newer ``MessageSender`` and the ``NotifyUser``.

MessageSender
=============

The ``MessageSender`` is used to send a pre-written message to a user. To
initialise the class pass in a context and a user-info for the person
who is to receive the message. The main method is::
          
    def send_message(self, subject, txtMessage, htmlMessage='', 
                        fromAddress=None, toAddresses=None)

If only the ``subject`` and ``txtMessage`` arguments are given then
the message will be sent to the default email addresses of the user
that was passed in when the message sender was initialised.

If the optional ``htmlMessage`` is provided then a multipart email
message will be created, with both the text and HTML forms of the
message set.

The ``fromAddress`` sets who sent the message. If omitted the email
address of the *Support* group is used. The system will fail an assertion
if it cannot find a user for the supplied ``fromAddress``.

Finally, the ``toAddress`` is a list of email addresses to send the
notification to. If omitted the system will use default (preferred)
addresses of the user that was passed in when the message sender was
initialised. The system will fail an assertion if a ``toAddress``
is used that does not belong to the user.
                        
Authors
=======

Michael JasonSmith <mpj17@onlinegroups.net> move the notification code
from Products.CustomUserFolder.CustomUser. The original code was writen
by Richard Waid <richard@iopen.net>.

