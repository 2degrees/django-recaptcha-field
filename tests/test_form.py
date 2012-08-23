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

from django.forms.fields import CharField
from django.forms.fields import EmailField
from django.forms.forms import Form
from django.http import HttpRequest
from nose.tools import assert_false
from nose.tools import eq_
from nose.tools import ok_

from django_recaptcha_field import create_form_subclass_with_recaptcha

from tests import FAKE_RECAPTCHA_CLIENT
from tests import RANDOM_REMOTE_IP


__all__ = [
    'TestFieldInitialization',
    'TestFormSubclass',
    ]


class TestFormSubclass(object):
    
    def test_inheritance(self):
        """The resulting form class is a subclass of the original form class"""
        ok_(
            issubclass(
                _MockRecaptchaProtectedRegistrationForm,
                _MockRegistrationForm,
                ),
            )
    
    def test_initialization(self):
        """
        The original form class still gets all the arguments it'd normally get
        at initialization.
        
        """
        request = _MockHttpRequest()
        form_data = object()
        form_files = object()
        
        form = _MockRecaptchaProtectedRegistrationForm(
            request,
            form_data,   # Consider positional arguments
            files=form_files,   # Consider named arguments
            )
        
        eq_(form_data, form.data)
        eq_(form_files, form.files)


class TestFieldInitialization(object):
    
    def test_ssl_request(self):
        """
        The widget uses SSL for the transmission of the challenge if the current
        request was made over SSL.
        
        """
        ssl_request = _MockHttpRequest(is_ssl_used=True)
        form = _MockRecaptchaProtectedRegistrationForm(ssl_request)
        
        recaptcha_widget = form.fields['recaptcha'].widget
        ok_(recaptcha_widget.transmit_challenge_over_ssl)
    
    def test_non_ssl_request(self):
        """
        The widget doesn't use SSL for the transmission of the challenge if the
        current request wasn't made over SSL.
        
        """
        non_ssl_request = _MockHttpRequest(is_ssl_used=False)
        form = _MockRecaptchaProtectedRegistrationForm(non_ssl_request)
        
        recaptcha_widget = form.fields['recaptcha'].widget
        assert_false(recaptcha_widget.transmit_challenge_over_ssl)
    
    def test_remote_ip(self):
        request = _MockHttpRequest(remote_addr=RANDOM_REMOTE_IP)
        form = _MockRecaptchaProtectedRegistrationForm(request)
        
        recaptcha_field = form.fields['recaptcha']
        eq_(RANDOM_REMOTE_IP, recaptcha_field.remote_ip)
    
    def test_additional_field_arguments(self):
        field_label = 'Are you human?'
        form_class = create_form_subclass_with_recaptcha(
            _MockRegistrationForm,
            FAKE_RECAPTCHA_CLIENT,
            additional_field_kwargs={'label': field_label},
            )
        form = form_class(_MockHttpRequest())
        
        recaptcha_field = form.fields['recaptcha']
        eq_(field_label, recaptcha_field.label)


#{ Stubs


class _MockHttpRequest(HttpRequest):
    
    def __init__(self, is_ssl_used=False, remote_addr=None):
        super(_MockHttpRequest, self).__init__()
        
        self.is_ssl_used = is_ssl_used
        self.META['REMOTE_ADDR'] = remote_addr
    
    def is_secure(self):
        return self.is_ssl_used


class _MockRegistrationForm(Form):

    full_name = CharField(max_length=255)
    
    email_address = EmailField(max_length=255)


_MockRecaptchaProtectedRegistrationForm = create_form_subclass_with_recaptcha(
    _MockRegistrationForm,
    FAKE_RECAPTCHA_CLIENT,
    )


#}
