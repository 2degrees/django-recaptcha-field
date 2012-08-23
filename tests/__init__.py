################################################################################
#
# Copyright (c) 2012, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
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

from os import environ

from recaptcha import RecaptchaClient


__all__ = [
    'FAKE_RECAPTCHA_CLIENT',
    'RANDOM_CHALLENGE_ID',
    'RANDOM_REMOTE_IP',
    'RANDOM_SOLUTION_TEXT',
    'setup',
    'teardown',
    ]


FAKE_RECAPTCHA_CLIENT = RecaptchaClient('private key', 'public_key')


RANDOM_SOLUTION_TEXT = 'hello world'
RANDOM_CHALLENGE_ID = 'abcde'
RANDOM_REMOTE_IP = '192.0.2.0'


def setup():
    environ['DJANGO_SETTINGS_MODULE'] = 'tests.django_settings'


def teardown():
    del environ['DJANGO_SETTINGS_MODULE']
