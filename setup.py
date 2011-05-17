# coding=utf-8
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

setup(name='gs.profile.notify',
    version=version,
    description="GroupServer Email Notifications",
    long_description=open("README.txt").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
      "Development Status :: 4 - Beta",
      "Environment :: Web Environment",
      "Framework :: Zope2",
      "Intended Audience :: Developers",
      "License :: Other/Proprietary License",
      "Natural Language :: English",
      "Operating System :: POSIX :: Linux"
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='notification user member email messagae',
    author='Michael JasonSmith',
    author_email='mpj17@onlinegroups.net',
    url='http://www.onlinegroups.net/',
    license='other',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs','gs.profile'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'gs.profile.email.base',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,)

