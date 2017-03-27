
# For our avatar images, we need to remove the Vary header so they actually
# get cached right.  HOWEVER session middleware adds it back in.
# We set a special skip_vary attribute to do this here.
class RemoveVaryCookieMiddleware(object):

    def process_response(self, request, response):
        if hasattr(response, 'skip_vary'):
            response['Vary'] = ''
        return response
