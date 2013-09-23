# -*- coding: utf-8 -*-
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

import codecs

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import force_unicode
from nose.tools import assert_false
from nose.tools import assert_not_equals
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp
from nose.tools import eq_
from nose.tools import ok_
from recaptcha import RECAPTCHA_CHARACTER_ENCODING
from recaptcha import RecaptchaInvalidChallengeError
from recaptcha import RecaptchaInvalidPrivateKeyError
from recaptcha import RecaptchaUnreachableError

from django_recaptcha_field import _RecaptchaField as RecaptchaField

from tests import FAKE_RECAPTCHA_CLIENT
from tests import RANDOM_CHALLENGE_ID
from tests import RANDOM_REMOTE_IP
from tests import RANDOM_SOLUTION_TEXT


__all__ = [
    'TestFieldValidation',
    'TestWidgetInitialization',
    ]


_RANDOM_RECAPTCHA_FIELD_VALUE = {
    'solution_text': RANDOM_SOLUTION_TEXT,
    'challenge_id': RANDOM_CHALLENGE_ID,
    }


def test_field_requireness():
    """The reCAPTCHA field is required in the form."""
    field = RecaptchaField(FAKE_RECAPTCHA_CLIENT, RANDOM_REMOTE_IP)

    ok_(field.required)


class TestWidgetInitialization(object):

    def test_recaptcha_client(self):
        field = RecaptchaField(FAKE_RECAPTCHA_CLIENT, RANDOM_REMOTE_IP)

        eq_(FAKE_RECAPTCHA_CLIENT, field.widget.recaptcha_client)

    def test_challenge_not_over_ssl(self):
        field = RecaptchaField(
            FAKE_RECAPTCHA_CLIENT,
            RANDOM_REMOTE_IP,
            transmit_challenge_over_ssl=False,
            )

        assert_false(field.widget.transmit_challenge_over_ssl)

    def test_challenge_over_ssl(self):
        field = RecaptchaField(
            FAKE_RECAPTCHA_CLIENT,
            RANDOM_REMOTE_IP,
            transmit_challenge_over_ssl=True,
            )

        ok_(field.widget.transmit_challenge_over_ssl)


class TestFieldValueConversion(object):

    _multiprocess_can_split_ = False   # The fixtures change global data

    def setup(self):
        self.recaptcha_client = \
            _OfflineVerificationClient(is_solution_correct=True)
        self.field = RecaptchaField(self.recaptcha_client, RANDOM_REMOTE_IP)

    def teardown(self):
        settings.DEFAULT_CHARSET = 'UTF-8'

    def test_no_value(self):
        field_value = None
        eq_(field_value, self.field.to_python(field_value))

    def test_value_in_encoding_not_supported_by_recaptcha(self):
        settings.DEFAULT_CHARSET = 'Latin-1'
        self._assert_different_codecs(
            RECAPTCHA_CHARACTER_ENCODING,
            settings.DEFAULT_CHARSET,
            )

        random_string_utf8 = u'profesión'.encode('UTF-8')
        random_string_bytes = random_string_utf8.decode('UTF-8')
        random_string_unsupported = \
            random_string_bytes.encode(settings.DEFAULT_CHARSET)
        field_value = {
            'solution_text': random_string_unsupported,
            'challenge_id': random_string_unsupported,
            }

        self.field.validate(field_value)
        eq_(random_string_utf8, self.recaptcha_client.solution_text)
        eq_(random_string_utf8, self.recaptcha_client.challenge_id)

    def test_unicode_value_in_supported_codec(self):
        settings.DEFAULT_CHARSET = RECAPTCHA_CHARACTER_ENCODING

        random_unicode_string = u'profesión'.encode(settings.DEFAULT_CHARSET)
        field_value = {
            'solution_text': random_unicode_string,
            'challenge_id': random_unicode_string,
            }

        self.field.validate(field_value)
        eq_(random_unicode_string, self.recaptcha_client.solution_text)
        eq_(random_unicode_string, self.recaptcha_client.challenge_id)

    def test_ascii_value(self):
        eq_(
            _RANDOM_RECAPTCHA_FIELD_VALUE,
            self.field.to_python(_RANDOM_RECAPTCHA_FIELD_VALUE),
            )

    #{ Utilities

    def _assert_different_codecs(self, codec1_name, codec2_name):
        """Assert that ``codec1_name`` and ``codec2_name`` aren't equivalent."""
        codec1_info = codecs.lookup(codec1_name)
        codec2_info = codecs.lookup(codec2_name)

        assert_not_equals(
            codec1_name,
            codec2_name,
            'Codecs {} and {} must be different'.format(
                codec1_name,
                codec2_name,
                ),
            )

    #}


class TestFieldValidation(object):

    def test_remote_api_unreachable(self):
        """
        Problems with the remote API call aren't considered validation errors.

        """
        self._assert_recaptcha_exception_propagates_on_validation(
            RecaptchaInvalidPrivateKeyError,
            )

    def test_invalid_private_key(self):
        """
        Using an invalid reCAPTCHA private key isn't considered a validation
        error.

        """
        self._assert_recaptcha_exception_propagates_on_validation(
            RecaptchaUnreachableError,
            )

    def test_no_solution_text_or_challenge_id(self):
        client = _OfflineVerificationClient()
        field_value = None

        self._assert_validation_error_raised(field_value, client, 'required')
        eq_(0, client.communication_attempts)

    def test_invalid_challenge_id(self):
        client = _ExceptionRaisingVerificationClient(
            RecaptchaInvalidChallengeError,
            )

        self._assert_validation_error_raised(
            _RANDOM_RECAPTCHA_FIELD_VALUE,
            client,
            'invalid',
            )

    def test_incorrect_solution(self):
        client = _OfflineVerificationClient(is_solution_correct=False)

        self._assert_validation_error_raised(
            _RANDOM_RECAPTCHA_FIELD_VALUE,
            client,
            'incorrect_solution',
            )

    def test_correct_solution(self):
        client = _OfflineVerificationClient(is_solution_correct=True)
        field = RecaptchaField(client, RANDOM_REMOTE_IP)

        field.validate(_RANDOM_RECAPTCHA_FIELD_VALUE)

    #{ Utilities

    def _assert_recaptcha_exception_propagates_on_validation(self, exception):
        client = _ExceptionRaisingVerificationClient(
            exception,
            )
        field = RecaptchaField(client, RANDOM_REMOTE_IP)

        with assert_raises(exception):
            field.validate(_RANDOM_RECAPTCHA_FIELD_VALUE)

    def _assert_validation_error_raised(self, field_value, client, error_code):
        field = RecaptchaField(client, RANDOM_REMOTE_IP)

        expected_error_message = force_unicode(field.error_messages[error_code])
        with assert_raises_regexp(ValidationError, expected_error_message):
            field.validate(field_value)

        should_mark_solution_as_incorrect = error_code == 'incorrect_solution'
        eq_(
            should_mark_solution_as_incorrect,
            field.widget.was_previous_solution_incorrect,
            )

    #}


#{ Stubs


class _OfflineVerificationClient(object):

    def __init__(self, is_solution_correct=None):
        super(_OfflineVerificationClient, self).__init__()

        self.is_solution_correct_ = is_solution_correct

        self.communication_attempts = 0

        self.solution_text = None
        self.challenge_id = None

    def is_solution_correct(self, solution_text, challenge_id, remote_ip):
        self.communication_attempts += 1

        self.solution_text = solution_text
        self.challenge_id = challenge_id

        return self.is_solution_correct_


class _ExceptionRaisingVerificationClient(object):

    def __init__(self, exception):
        super(_ExceptionRaisingVerificationClient, self).__init__()

        self.exception = exception

    def is_solution_correct(self, solution_text, challenge_id, remote_ip):
        raise self.exception


#}
