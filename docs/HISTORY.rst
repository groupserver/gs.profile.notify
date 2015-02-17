Changelog
=========

3.2.2 (2015-02-17)
------------------

* Added some Unicode robustness

3.2.1 (2015-02-04)
------------------

* Added a ``Date`` header

3.2.0 (2014-09-23)
------------------

* Switching to GitHub_ as the primary repository
* Using the ``@implementer`` class decorator rather than the
  ``implements`` statement
* Unicode fixes to the audit trail
* Updating the documentation

.. _gs.profile.notify: https://github.com/groupserver/gs.profile.notify

3.1.3 (2014-06-11)
------------------

* Added more error checking

3.1.2 (2014-02-28)
------------------

* Updated the ``To`` and ``From`` headers
* Updated the documentation on the *Reset password* notification

3.1.1 (2014-01-29)
------------------

* Updated documentation

3.1.0 (2013-10-21)
------------------

* Better auditing
* Ensuring that the ``gs.profile.notifiy.NotifiyUser`` is exposed
  to ZMI-side stripts

.. _gs.email: https://github.com/groupserver/gs.email

2.1.0 (2012-06-22)
------------------

* Update to SQLAlchemy_

.. _SQLAlchemy: http://www.sqlalchemy.org/

2.0.3 (2012-03-27)
------------------

* Updating the documentation

2.0.2 (2012-02-07)
------------------

* Using the ``@Lazy`` decorator in the message sender

2.0.1 (2012-01-18)
------------------

* Added to the documentation
* Fixing some context issues

2.0.0 (2011-05-18)
------------------

* Added the ability to send HTML formatted email notifications
* Made the ``From`` address optional

1.1.0 (2011-01-18)
------------------

* Added an ``EmailUser`` class
* Following the `gs.profile.email.base`_ code

.. _gs.profile.email.base:
   https://github.com/groupserver/gs.profile.email.base

1.0.2 (2010-09-28)
------------------

* Getting the site-information more reliably
* Fixing an overly zealous assert

1.0.1 (2010-07-09)
------------------

* Removing a ``<five:implements>`` declaration from the ZCML

1.0.0 (2010-04-15)
------------------

Initial version. Prior to the creation of this product email
notifications were handled by `Products.CustomUserFolder`_ and
templates in the ``Templates/email/notifications`` folder of the
ZMI. The ``NotifyUser`` code was originally written by was
written by `Richard Waid <richard@iopen.net>`_.

.. _Products.CustomUserFolder:
   https://github.com/groupserver/Products.CustomUserFolder

..  LocalWords:  Changelog CustomUserFolder ZMI github groupserver ZCML
..  LocalWords:  EmailUser
