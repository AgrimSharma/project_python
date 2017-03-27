from requests_aws4auth import AWS4Auth


class StrBasedAWS4Auth(AWS4Auth):
    """We ran into a problem using elastic search in combination with AWS authentication.  There was a place, deep inside
       the httplib library where the headers and the body were concatenated.  If they differed in character encoding (a unicode
       plus a str) it could fail.  There wasn't a good way to modify it directly, but we can modify our auth class so it always
       gives us str based headers in the request, which fixes the problem.
    """
    def __init__(self, *args, **kwargs):
        AWS4Auth.__init__(self, *args, **kwargs)

    def __call__(self, req):
        req = super(StrBasedAWS4Auth, self).__call__(req)
        req.headers = {str(k): str(v) for k,v in req.headers.iteritems()}
        return req
