###############################################################################
#
# Copyright (C) 2014-2016 PyWPS Development Team, represented by
# PyWPS Project Steering Committee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
###############################################################################

import unittest
import lxml
import lxml.etree
from pywps.app import Process, Service
from pywps import WPS, OWS
from tests.common import assert_pywps_version, client_for

class BadRequestTest(unittest.TestCase):

    def test_bad_http_verb(self):
        client = client_for(Service())
        resp = client.put('')
        assert resp.status_code == 405  # method not allowed

    def test_bad_request_type_with_get(self):
        client = client_for(Service())
        resp = client.get('?Request=foo')
        assert resp.status_code == 400

    def test_bad_service_type_with_get(self):
        client = client_for(Service())
        resp = client.get('?service=foo')

        exception = resp.xpath('/ows:ExceptionReport'
                                '/ows:Exception')

        assert resp.status_code == 400
        assert exception[0].attrib['exceptionCode'] == 'InvalidParameterValue'

    def test_bad_request_type_with_post(self):
        client = client_for(Service())
        request_doc = WPS.Foo()
        resp = client.post_xml('', doc=request_doc)
        assert resp.status_code == 400


class CapabilitiesTest(unittest.TestCase):

    def setUp(self):
        def pr1(): pass
        def pr2(): pass
        self.client = client_for(Service(processes=[Process(pr1, 'pr1', 'Process 1'), Process(pr2, 'pr2', 'Process 2')]))

    def check_capabilities_response(self, resp):
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] == 'text/xml'
        title = resp.xpath_text('/wps:Capabilities'
                                '/ows:ServiceIdentification'
                                '/ows:Title')
        assert title != ''
        names = resp.xpath_text('/wps:Capabilities'
                                '/wps:ProcessOfferings'
                                '/wps:Process'
                                '/ows:Identifier')
        assert sorted(names.split()) == ['pr1', 'pr2']

    def test_get_request(self):
        resp = self.client.get('?Request=GetCapabilities&service=WpS')
        self.check_capabilities_response(resp)

        # case insesitive check
        resp = self.client.get('?request=getcapabilities&service=wps')
        self.check_capabilities_response(resp)

    def test_post_request(self):
        request_doc = WPS.GetCapabilities()
        resp = self.client.post_xml(doc=request_doc)
        self.check_capabilities_response(resp)

    def test_get_bad_version(self):
        resp = self.client.get('?request=getcapabilities&service=wps&acceptversions=2001-123')
        exception = resp.xpath('/ows:ExceptionReport'
                                '/ows:Exception')
        assert resp.status_code == 400
        assert exception[0].attrib['exceptionCode'] == 'VersionNegotiationFailed'

    def test_post_bad_version(self):
        acceptedVersions_doc = OWS.AcceptVersions(
                OWS.Version('2001-123'))
        request_doc = WPS.GetCapabilities(acceptedVersions_doc)
        resp = self.client.post_xml(doc=request_doc)
        exception = resp.xpath('/ows:ExceptionReport'
                                '/ows:Exception')

        assert resp.status_code == 400
        assert exception[0].attrib['exceptionCode'] == 'VersionNegotiationFailed'

    def test_pywps_version(self):
        resp = self.client.get('?service=WPS&request=GetCapabilities')
        assert_pywps_version(resp)


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(BadRequestTest),
        loader.loadTestsFromTestCase(CapabilitiesTest),
    ]
    return unittest.TestSuite(suite_list)
