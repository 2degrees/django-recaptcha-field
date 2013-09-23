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

from nose.tools import assert_false
from nose.tools import eq_
from nose.tools import ok_

from django_recaptcha_field import _RecaptchaWidget as RecaptchaWidget

from tests import FAKE_RECAPTCHA_CLIENT
from tests import RANDOM_CHALLENGE_ID
from tests import RANDOM_SOLUTION_TEXT


__all__ = [
    'TestWidgetDataExtraction',
    'TestWidgetRendering',
    ]


_RECAPTCHA_INCORRECT_SOLUTION_URL_QUERY = 'error=incorrect-captcha-sol'


_FAKE_FILES_DATA = {}
_FAKE_FIELD_NAME = 'field_name'
_FAKE_FIELD_VALUE = None
_FAKE_FIELD_ATTRIBUTES = {}


class TestWidgetDataExtraction(object):

    def test_no_solution(self):
        """The field is considered to be absent if there's no solution."""
        widget = RecaptchaWidget(FAKE_RECAPTCHA_CLIENT)

        form_data = {'recaptcha_challenge_field': RANDOM_CHALLENGE_ID}
        field_value = widget.value_from_datadict(
            form_data,
            _FAKE_FILES_DATA,
            _FAKE_FIELD_NAME,
            )
        eq_(None, field_value)

    def test_no_challenge(self):
        """The field is considered to be absent if there's no challenge Id."""
        widget = RecaptchaWidget(FAKE_RECAPTCHA_CLIENT)

        form_data = {'recaptcha_response_field': RANDOM_SOLUTION_TEXT}
        field_value = widget.value_from_datadict(
            form_data,
            _FAKE_FILES_DATA,
            _FAKE_FIELD_NAME,
            )
        eq_(None, field_value)

    def test_solution_and_challenge(self):
        widget = RecaptchaWidget(FAKE_RECAPTCHA_CLIENT)

        form_data = {
            'recaptcha_response_field': RANDOM_SOLUTION_TEXT,
            'recaptcha_challenge_field': RANDOM_CHALLENGE_ID,
            }
        field_value = widget.value_from_datadict(
            form_data,
            _FAKE_FILES_DATA,
            _FAKE_FIELD_NAME,
            )

        ok_('solution_text' in field_value)
        eq_(RANDOM_SOLUTION_TEXT, field_value['solution_text'])

        ok_('challenge_id' in field_value)
        eq_(RANDOM_CHALLENGE_ID, field_value['challenge_id'])


class TestWidgetRendering(object):

    def test_previous_solution_incorrect(self):
        widget = RecaptchaWidget(FAKE_RECAPTCHA_CLIENT)
        widget.was_previous_solution_incorrect = True

        widget_markup = widget.render(
            _FAKE_FIELD_NAME,
            _FAKE_FIELD_VALUE,
            _FAKE_FIELD_ATTRIBUTES,
            )

        ok_(_RECAPTCHA_INCORRECT_SOLUTION_URL_QUERY in widget_markup)

    def test_previous_solution_correct(self):
        widget = RecaptchaWidget(FAKE_RECAPTCHA_CLIENT)

        widget_markup = widget.render(
            _FAKE_FIELD_NAME,
            _FAKE_FIELD_VALUE,
            _FAKE_FIELD_ATTRIBUTES,
            )

        assert_false(_RECAPTCHA_INCORRECT_SOLUTION_URL_QUERY in widget_markup)

    def test_challenge_not_over_ssl(self):
        widget = RecaptchaWidget(
            FAKE_RECAPTCHA_CLIENT,
            transmit_challenge_over_ssl=False,
            )

        widget_markup = widget.render(
            _FAKE_FIELD_NAME,
            _FAKE_FIELD_VALUE,
            _FAKE_FIELD_ATTRIBUTES,
            )

        assert_false('https://' in widget_markup)
        ok_('http://' in widget_markup)

    def test_challenge_over_ssl(self):
        widget = RecaptchaWidget(
            FAKE_RECAPTCHA_CLIENT,
            transmit_challenge_over_ssl=True,
            )

        widget_markup = widget.render(
            _FAKE_FIELD_NAME,
            _FAKE_FIELD_VALUE,
            _FAKE_FIELD_ATTRIBUTES,
            )

        assert_false('http://' in widget_markup)
        ok_('https://' in widget_markup)
