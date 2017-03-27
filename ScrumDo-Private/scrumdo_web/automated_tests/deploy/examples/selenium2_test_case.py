class Selenium2TestCase(TestCase):

    def report_pass_fail(self):
        base64string = base64.encodestring('%s:%s' % (config['username'],
                                                      config['access-key']))[:-1]
        result = json.dumps({'passed': self._exc_info() == (None, None, None)})
        connection =  httplib.HTTPConnection(self.config['host'])
        connection.request('PUT', '/rest/v1/%s/jobs/%s' % (self.config['username'],
                                                           self.driver.session_id),
                           result,
                           headers={"Authorization": "Basic %s" % base64string})
        result = connection.getresponse()
        return result.status == 200

    def tearDown(self):
        self.report_pass_fail()
        self.driver.quit()
