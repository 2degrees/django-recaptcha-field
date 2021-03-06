################################################################################
#
# Copyright (c) 2012, 2degrees Limited <2degrees-floss@googlegroups.com>.
# All Rights Reserved.
#
# This file is part of django-recaptcha-field
# <http://packages.python.org/django-recaptcha-field/>, which is subject to the
# provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
################################################################################

import os

from setuptools import setup


_branch_path = os.path.abspath(os.path.dirname(__file__))
_readme = open(os.path.join(_branch_path, 'README.txt')).read()
_version = open(os.path.join(_branch_path, 'VERSION.txt')).readline().rstrip()


setup(
    name='django-recaptcha-field',
    version=_version,
    description='Easy-to-use, highly extensible and well documented reCAPTCHA '
        'plugin for Django forms',
    long_description=_readme,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
        ],
    keywords='recaptcha captcha django',
    author='2degrees Limited',
    author_email='2degrees-floss@googlegroups.com',
    url='http://packages.python.org/django-recaptcha-field/',
    license='BSD (http://dev.2degreesnetwork.com/p/2degrees-license.html)',
    py_modules=['django_recaptcha_field'],
    zip_safe=False,
    install_requires=['django >= 1.3', 'recaptcha >= 1.0rc1'],
    tests_require=['coverage', 'nose'],
    test_suite='nose.collector',
    )
