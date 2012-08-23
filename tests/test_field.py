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

from django.core.exceptions import ValidationError
from django.utils.encoding import force_unicode
from nose.tools import assert_false
from nose.tools import assert_raises
from nose.tools import assert_raises_regexp
from nose.tools import eq_
from nose.tools import ok_
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
        eq_(0, client.communication_attemps)
    
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
    
    #}


#{ Stubs


class _OfflineVerificationClient(object):
    
    def __init__(self, is_solution_correct=None):
        super(_OfflineVerificationClient, self).__init__()
        
        self.is_solution_correct_ = is_solution_correct
        self.communication_attemps = 0
    
    def is_solution_correct(self, solution_text, challenge_id, remote_ip):
        self.communication_attemps += 1
        
        return self.is_solution_correct_


class _ExceptionRaisingVerificationClient(object):
    
    def __init__(self, exception):
        super(_ExceptionRaisingVerificationClient, self).__init__()
        
        self.exception = exception
    
    def is_solution_correct(self, solution_text, challenge_id, remote_ip):
        raise self.exception


#}
