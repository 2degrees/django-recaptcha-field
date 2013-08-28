*************************************
reCAPTCHA integration in Django forms
*************************************

.. module:: django_recaptcha_field

:Latest release: |release|
:Download: `<http://pypi.python.org/pypi/django-recaptcha-field/>`_
:Development: `<https://github.com/2degrees/django-recaptcha-field>`_
:Author: `2degrees Limited <http://dev.2degreesnetwork.com/>`_

This is the easy-to-use, highly extensible and well documented `reCAPTCHA
<https://www.google.com/recaptcha/>`_ plugin for Django forms based on the
:mod:`recaptcha` Python client.

This library lets your add a reCAPTCHA field to any form class. This field
is rendered with a widget that supports non-JavaScript challenges and
`customization <https://developers.google.com/recaptcha/docs/customization>`_.


Tutorial
========

Before you can create form classes that have a reCAPTCHA field, you need a
:class:`recaptcha.RecaptchaClient` instance which can be created as follows::

    from recaptcha import RecaptchaClient
    recaptcha_client = RecaptchaClient('private key', 'public key')

You can then use :func:`create_form_subclass_with_recaptcha` to create a
derivative form class with a reCAPTCHA field like so::

    from django_recaptcha_field import create_form_subclass_with_recaptcha
    from my_app.forms import MyForm
    
    MyRecaptchaProtectedForm = create_form_subclass_with_recaptcha(
        MyForm,
        recaptcha_client,
        )

Except for the widget and the required state of the field, you can override
other field attributes such as the label and the error messages::

    MyRecaptchaProtectedForm = create_form_subclass_with_recaptcha(
        MyForm,
        recaptcha_client,
        {'label': 'Are you human?'},
        )


The resulting class requires the request as the first argument when initialized
and any additional arguments will be passed on to the constructor of the base
form class. The request is required to extract data necessary for the rendering
and validation of the field; namely, the remote IP address and whether such a
request was made over SSL.


Validation
----------

Forms can be validated as usual::

    def my_view(request):
        if request.method == 'POST':
            form = MyRecaptchaProtectedForm(request, request.POST)
            
            if form.is_valid():
                process_form_data(form.cleaned_data)
        else:
            form = MyRecaptchaProtectedForm(request)
        
        # (...)
        
        return response

with one caveat: Some :mod:`recaptcha` exceptions may propagate through
``form.is_valid()`` upon validation of the reCAPTCHA field. This is intended
to give developers control over the handling of the different errors that may
occur.

The field handles :exc:`recaptcha.RecaptchaInvalidChallengeError` by turning it
into a validation error. All the other exceptions, such as
:exc:`recaptcha.RecaptchaUnreachableError`, will propagate. So views using these
form subclasses may look like this::

    from logging import getLogger
    from django.contrib import messages
    
    LOGGER = getLogger(__name__)
    
    def my_view(request):
        if request.method == 'POST':
            form = MyRecaptchaProtectedForm(request, request.POST)
            
            try:
                is_form_valid = form.is_valid()
            except RecaptchaUnreachableError:
                # Bypass reCAPTCHA silently
                form = MyForm(request.POST)
                is_form_valid = form.is_valid()
            except RecaptchaException as exc:
                LOGGER.exception(exc)
                messages.add_message(request, messages.ERROR, 'Try again later')
                form = None
                is_form_valid = False
            
            if is_form_valid:
                process_form_data(form.cleaned_data)
        else:
            form = MyRecaptchaProtectedForm(request)
        
        # (...)
        
        return response


Presentation
------------

The form subclass created by :func:`create_form_subclass_with_recaptcha` has a
field named ``recaptcha`` the behaves like any other field. Use the `safe
<https://docs.djangoproject.com/en/stable/ref/templates/builtins/#safe>`_ filter to 
display the field::

    <form action="..." method="...">
        ...
        {{ form.recaptcha | safe }}
        {{ form.recaptcha.errors }}
        ...
    </form>

The widget for the reCAPTCHA field will make sure that the reCAPTCHA challenge
is transmitted over SSL if the request was made over SSL, and vice versa.

If you'd like to `customize
<https://developers.google.com/recaptcha/docs/customization>`_ the challenge,
you'd need to set the so-called ``RecaptchaOptions`` on the client. See:
:class:`recaptcha.RecaptchaClient`.


Client API
==========

.. autofunction:: create_form_subclass_with_recaptcha


Support
=======

For general reCAPTCHA support, please visit the `reCAPTCHA developers' site
<https://developers.google.com/recaptcha/>`_. Please visit the :mod:`recaptcha`
library documentation if you require any assistance with it.

For suggestions and questions about this library, please use our `2degrees-floss
mailing list <http://groups.google.com/group/2degrees-floss/>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

