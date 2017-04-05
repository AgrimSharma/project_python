def get_field(self):
    #sort_field_name = {'usr':'username','dj':'date_joined'}
    try:
        field = self.REQUEST['sort']
        #  field = sort_field_name[self.REQUEST['sort']]
    except (KeyError, ValueError, TypeError):
        field = ''
    return (self.direction == 'desc' and '-' or '') + field

def get_direction(self):
    try:
        return self.REQUEST['dir']
    except (KeyError, ValueError, TypeError):
        return 'desc'

class SortingMiddleware(object):
    """
    Inserts a variable representing the field (with direction of sorting)
    onto the request object if it exists in either **GET** or **POST** 
    portions of the request.
    """
    def process_request(self, request):
        request.__class__.field = property(get_field)
        request.__class__.direction = property(get_direction)