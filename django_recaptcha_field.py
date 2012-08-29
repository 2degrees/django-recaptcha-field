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

from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.fields import Field
from django.forms.widgets import Widget
from recaptcha import RECAPTCHA_CHARACTER_ENCODING
from recaptcha import RecaptchaInvalidChallengeError


__all__ = ['create_form_subclass_with_recaptcha']


def create_form_subclass_with_recaptcha(
    base_form_class,
    recaptcha_client,
    additional_field_kwargs=None,
    ):
    """
    Create a subclass of ``base_form_class`` with an extra field for the
    reCAPTCHA challenge.
    
    :param base_form_class: The parent form class
    :param recaptcha_client:
    :type recaptcha_client: :class:`recaptcha.RecaptchaClient`
    :param additional_field_kwargs: Any additional arguments for the
        constructor of the form field
    :type additional_field_kwargs: :class:`dict`
    
    """
    
    additional_field_kwargs = additional_field_kwargs or {}
    
    class RecaptchaProtectedForm(base_form_class):
        
        def __init__(self, request, *args, **kwargs):
            super(RecaptchaProtectedForm, self).__init__(*args, **kwargs)
            
            self.fields['recaptcha'] = _RecaptchaField(
                recaptcha_client,
                request.META['REMOTE_ADDR'],
                request.is_secure(),
                **additional_field_kwargs
                )
    
    return RecaptchaProtectedForm


class _RecaptchaField(Field):
    
    default_error_messages = {
        'incorrect_solution': 'Your solution to the CAPTCHA was incorrect',
        }
    
    def __init__(
        self,
        recaptcha_client,
        remote_ip,
        transmit_challenge_over_ssl=False,
        **kwargs
        ):
        widget = _RecaptchaWidget(recaptcha_client, transmit_challenge_over_ssl)
        super(_RecaptchaField, self).__init__(
            widget=widget,
            required=True,
            **kwargs
            )
        
        self.recaptcha_client = recaptcha_client
        self.remote_ip = remote_ip
    
    def validate(self, value):
        super(_RecaptchaField, self).validate(value)
        
        solution_text = _encode_input_for_recaptcha(value['solution_text'])
        challenge_id = _encode_input_for_recaptcha(value['challenge_id'])
        try:
            is_solution_correct = self.recaptcha_client.is_solution_correct(
                solution_text,
                challenge_id,
                self.remote_ip,
                )
        except RecaptchaInvalidChallengeError:
            raise ValidationError(self.error_messages['invalid'])
        
        if not is_solution_correct:
            self.widget.was_previous_solution_incorrect = True
            raise ValidationError(self.error_messages['incorrect_solution'])


class _RecaptchaWidget(Widget):
    
    def __init__(self, recaptcha_client, transmit_challenge_over_ssl=False):
        super(_RecaptchaWidget, self).__init__()
        
        self.recaptcha_client = recaptcha_client
        self.transmit_challenge_over_ssl = transmit_challenge_over_ssl
        
        self.was_previous_solution_incorrect = False
    
    def value_from_datadict(self, data, files, name):
        solution_text = data.get('recaptcha_response_field')
        challenge_id = data.get('recaptcha_challenge_field')
        
        if solution_text and challenge_id:
            value = {
                'solution_text': solution_text,
                'challenge_id': challenge_id,
                }
        else:
            value = None
        
        return value
    
    def render(self, name, value, attrs=None):
        challenge_markup = self.recaptcha_client.get_challenge_markup(
            self.was_previous_solution_incorrect,
            self.transmit_challenge_over_ssl,
            )
        return challenge_markup


#{ Utiltities


def _encode_input_for_recaptcha(string):
    string_bytes = string.decode(settings.DEFAULT_CHARSET)
    string_encoded = string_bytes.encode(RECAPTCHA_CHARACTER_ENCODING)
    return string_encoded


#}
