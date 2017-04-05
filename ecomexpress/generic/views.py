import json
import requests
from jsonview.decorators import json_view
from location.models import Pincode


@json_view
def getpincode_info(request):
    address = request.GET.get('address')
    result = requests.get("http://www.getpincode.info/api/pincode", 
                          params={'q': address})
    data = json.loads(result._content)
    try:
        pin = Pincode.objects.get(pincode=data.get('pincode'))
        sc = pin.service_center
        return {'code': sc.center_shortcode, 'sc_id': sc.id, 'success': True}
    except:
        return {'success': False}
