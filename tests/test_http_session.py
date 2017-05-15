from unittest import TestCase
from mock import Mock
from mock import patch

from nsxramlclient.client import NsxClient
from nsxramlclient.exceptions import XMLParseError
from test_settings import NSX_RAML_PATH


class TestHttpSession(TestCase):
    """
    This test case tests Whether or not http_session.py Handles
    XML Parse Error Correctly when NSX Manager returns broken XML.
    """

    def test_raise_xml_parse_error(self):

        # Define Dummy Response Data from NSX_Manager
        dummy_response = Mock()
        dummy_response.status_code = 200
        dummy_response.headers = {'content-type': 'application/xml'}
        dummy_response.content = b'<?xml version="1.0" encoding="UTF-8"?>\n<dummy>brokenXML'

        # Override return val of request requests.Session.request
        # In order to obtain corrupted xml response
        with patch(target='requests.Session.request') as req:
            req.return_value = dummy_response

            # Initialize NSXClient session with 3 different fail_mode
            client_session_raise_on_error = NsxClient(nsxmanager='dummy',
                                                      nsx_username='dummy',
                                                      nsx_password='dummy',
                                                      raml_file=NSX_RAML_PATH,
                                                      fail_mode='raise'
                                                      )

            client_session_exit_on_error = NsxClient(nsxmanager='dummy',
                                                     nsx_username='dummy',
                                                     nsx_password='dummy',
                                                     raml_file=NSX_RAML_PATH,
                                                     fail_mode='exit'
                                                     )

            client_session_continue_on_error = NsxClient(nsxmanager='dummy',
                                                         nsx_username='dummy',
                                                         nsx_password='dummy',
                                                         raml_file=NSX_RAML_PATH,
                                                         fail_mode='continue'
                                                         )

            # This resource can be changed as far as it's in RAML definition.
            target_resource = 'dfwConfig'
            query_parameters = {'ruleType': 'LAYER3'}

            # Assert1 : Confirm if XMLParseError successfully raised in fail_mode='raise'
            with self.assertRaises(excClass=XMLParseError) as e_raise:

                raw_response = client_session_raise_on_error.read(target_resource,
                                                                  query_parameters_dict=query_parameters)
            self.assertTrue(isinstance(e_raise.exception, XMLParseError))

            # Assert2 : Confirm if program exits in fail_mode='exit'
            with self.assertRaises(excClass=SystemExit) as e_exit:

                raw_response = client_session_exit_on_error.read(target_resource,
                                                                 query_parameters_dict=query_parameters)
            self.assertTrue(isinstance(e_exit.exception, SystemExit))

            # Assert3 : Confirm read method returns None body when fail_mode='continue'
            raw_response = client_session_continue_on_error.read(target_resource,
                                                                 query_parameters_dict=query_parameters)
            self.assertIsNone(raw_response['body'])
