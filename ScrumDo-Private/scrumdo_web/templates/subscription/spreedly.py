import urllib2

SITE_NAME = "scrumdo"
API_TOKEN = "89887637ce899ba9b7dbb91f86dacc77432a089f"


def getTransactions( since_id):
    url = "https://subs.pinpayments.com/api/v4/%s/transactions.xml?since_id=%d" % (SITE_NAME, since_id)
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm='Web Password',
                              uri='https://subs.pinpayments.com/api',
                              user=API_TOKEN,
                              passwd='x')
    opener = urllib2.build_opener(auth_handler)

    urllib2.install_opener(opener)
    raw_data = urllib2.urlopen(url)
    logger.debug(raw_data)
    data = parse( raw_data  )
    return data