import re

from django.http import HttpResponseRedirect
from authentication.models import EmployeeMaster, is_user_allowed_access


class VerifyAccessMiddleware(object):

    def process_request(self, request):
        full_url = request.get_full_path()

        if full_url in ["/sorter_api/success_csv/","/sorter_api/failed_csv/",'/api/lastmile/update?strXML=', '/authentication/logout_view/', '/authentication/update_password/', '/track_me/api/mawb/',  '/track_me/api/awb/',  '/track_me/api/mawbd/']:
            return None

        app_url = re.match(r'\/\w+\/', full_url)
        if not app_url:
            return None

        url = app_url.group()[1:-1]

        if url in ['admin', 'track_shipment', 'static', 'mobile','api','sorter_api','apiv2','shacti_api']:
            return None
        try:
            request.user.employeemaster
        except (AttributeError, EmployeeMaster.DoesNotExist):
            return HttpResponseRedirect('/')

        if is_user_allowed_access(request.user, url):
            return None
        else:
            return HttpResponseRedirect('/access_denied/')
