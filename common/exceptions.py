import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.reverse import reverse
from rest_framework.views import exception_handler as drf_exception_handler

from drf_problems.utils import register

logger = logging.getLogger('rallz_problems')


def exception_handler(exc, context):
    # Convert Django exceptions (from DRF).
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif not isinstance(exc, exceptions.APIException):
        # Fallback handler to convert remaining exceptions to API exception.
        logger.exception(exc)
        exc = exceptions.APIException(exc)

    request = context['request']
    response = drf_exception_handler(exc, context)
    data = response.data

    problem_title = getattr(exc, 'title', exc.default_detail)
    problem_status = response.status_code
    problem_code = getattr(exc, 'code', exc.default_code)
    # problem_type = reverse('drf_problems:error-documentation',
    #                        kwargs={'code': problem_code}, request=request)
    if isinstance(data, dict):
        data['title'] = problem_title
        data['status'] = problem_status
        data['code'] = problem_code
    else:
        data = dict(errors=response.data, code=problem_code, title=problem_title,
                    status=problem_status)
    try:
        if request.accepted_renderer.format == 'json':
            response.content_type = 'application/problem+json'
    except AttributeError:
        pass
    response.data = data

    return response


class DetailDictMixin:
    def __init__(self, detail=None, code=None):
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """
        detail_dict = {'detail': self.default_detail,
                       'code': self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict['detail'] = detail

        if code is not None:
            detail_dict['code'] = code

        super().__init__(detail_dict)
