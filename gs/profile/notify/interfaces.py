# coding=utf-8
from zope.interface import Interface

class IGSNotifyUser( Interface ):
  
    def send_notification(n_type, n_id='default', n_dict=None, email_only=()): #@NoSelf
        '''Send a standard notification to the user.
        
ARGUMENTS
---------

``n_type``
    The type of notification to send, specified as a string.
    
``n_id``
    The ID of the notification template, specified as a string. Defaults
    to ``default``.

``n_dict``
    A dictionary of parameters to pass to the notification template.
    
``email_only``
    If specified, the notification will only be sent to the user's email
    addresses that are listed.

RETURNS
-------

None.

SIDE EFFECTS
------------

An email message is sent, from the standard support email address to the
user's verified email addresses. If ``email_only`` is specified then the 
message is only sent to the email addresses in that list, regardless of
whether the address is verified or not.'''

    def send_message(message, email_to, email_from=''): #@NoSelf
    '''Send a message to an user's address
    
ARGUMENTS
---------

```message```
    The message to send to the user.

``email_to``
    The email address to send the message to.
    
``email_from``
    The email address to send the message from. If not specified the
    support email address for the site will be used.
    
RETURNS
-------
    
None.

SIDE EFFECTS
------------
The message from ``email_from`` to ``email_to`` will be sent.'''

