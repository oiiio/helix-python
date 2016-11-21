"""
Tests for `helix` module.
"""
import os.path
import responses
from helix import EventTypes, Scope

CUSTOMER_INFO = {
    'email': 'joe@example.com',
    'first_name': 'Test',
    'last_name': 'User',
    'support_id': 'US-X3SY-3PD9T'
}

EVENTS_BODY = """{
  "events": [
    {
      "sequenceNum": 2,
      "eventType": "accountUpdate",
      "pacId": "PC-XIMPMZE75Q5XQHDKS6EC3EDSWAQJF25A",
      "timestamp": "2016-08-05T21:08:35Z"
    },
    {
      "sequenceNum": 4,
      "eventType": "sampleStatusUpdate",
      "pacId": "PC-XIMPMZE75Q5XQHDKS6EC3EDSWAQJF25A",
      "timestamp": "2016-08-05T21:08:42Z"
    },
    {
      "sequenceNum": 6,
      "eventType": "sampleStatusUpdate",
      "pacId": "PC-XIMPMZE75Q5XQHDKS6EC3EDSWAQJF25A",
      "timestamp": "2016-08-05T21:08:48Z"
    },
    {
      "sequenceNum": 8,
      "eventType": "sampleStatusUpdate",
      "pacId": "PC-XIMPMZE75Q5XQHDKS6EC3EDSWAQJF25A",
      "timestamp": "2016-08-05T21:08:54Z"
    },
    {
      "sequenceNum": 15,
      "eventType": "accountUpdate",
      "pacId": "PC-VCIOSK47ERXXIBPO5ZBOMW2HSNCQETCY",
      "timestamp": "2016-08-05T21:44:20Z"
    },
    {
      "sequenceNum": 16,
      "eventType": "accountUpdate",
      "pacId": "PC-VCIOSK47ERXXIBPO5ZBOMW2HSNCQETCY",
      "timestamp": "2016-08-05T22:53:40Z"
    },
    {
      "sequenceNum": 18,
      "eventType": "accessRevoked",
      "pacId": "PC-VCIOSK47ERXXIBPO5ZBOMW2HSNCQETCY",
      "timestamp": "2016-09-05T22:53:40Z"
    }

  ]
}
"""

LOGIN_BODY = """{
  "access_token": "eyJhbGciOiJFUxUxMiIsInS5cCI6IkpXVCJ9.eyJhcHBJZCI6IkFQLU02QTdGMk9KUUJWUlY2Q0dZNlJTWlZMNjI0Mk4zUlYyIiwiZXhwIjoxNDc5MjQxMDg3LCJzY29wZSI6ImlkZW50aXR5Iiwic3ViIjoiQ0wtN0lDQ0RUVE1HV0s3VkhUSklIQ1BXWlo3RUVaQklEN1oifQ.ANoawb4uBZbyY0g8RZThkaCap-e5wp08oskYJ70don_hx6q8D7fyireoNbWAa72zESrhEWAikoKn23g1pB6CDCJ0AI-XzKSnz3_r8qBedOLRYsruSp1OmRez6FOXEwJYaVJSpgRBX3VSwy3iMTwTl8_ysF3L8M3FmurX4uXD8RglyYoy",
  "expires_in": 1800,
  "scope": "identity",
  "token_type": "Bearer"
}
"""

CUSTOMER_INFO_BODY = """{"supportId":"US-X3SY-3PD9T","firstName":"Test","lastName":"User","email":"joe@example.com"}"""

SAMPLE_STATUS_BODY = """{
  "sampleStatus": [
    {
      "timestamp": "2016-11-15T01:32:08Z",
      "status": "Data Delivery Complete"
    },
    {
      "timestamp": "2016-11-15T01:28:34Z",
      "status": "Data Delivery Complete"
    },
    {
      "timestamp": "2016-11-15T00:17:56Z",
      "status": "Data Delivery Complete"
    },
    {
      "timestamp": "2016-11-15T00:16:41Z",
      "status": "Data Delivery Complete"
    }
  ]
}"""


class TestHelixApi:
    PACID = "PC-VCIOSK47ERXXIBPO5ZBOMW2HSNCQETCY"

    def test_login(self, helix):

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST, 'https://api.staging.helix.com/v0/oauth/access_token',
                body=LOGIN_BODY, status=200, content_type='application/json')

            data = helix.login(scope=Scope.IDENTITY)
            assert helix.scope == Scope.IDENTITY
            assert 'access_token' in data
            assert 'expires_in' in data and data['expires_in'] == 1800
            assert 'scope' in data and data['scope'] == Scope.IDENTITY
            assert 'token_type' in data and data['token_type'] == "Bearer"

    def test_events(self, helix):

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, 'https://api.staging.helix.com/v0/events',
                body=EVENTS_BODY, status=200, content_type='application/json')

            events = helix.events(event_type=EventTypes.accountUpdate)
            assert events is not None
            assert len(events) == 7

    def test_customer_info(self, helix):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, 'https://api.staging.helix.com/v0/customers/{}'.format(self.PACID),
                body=CUSTOMER_INFO_BODY, status=200, content_type='application/json')

            info = helix.customer_info(self.PACID)
            assert info is not None
            assert info == CUSTOMER_INFO

    def test_sample_status(self, helix):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, 'https://api.staging.helix.com/v0/customers/{}/samplestatus'.format(self.PACID),
                body=SAMPLE_STATUS_BODY, status=200, content_type='application/json')

            statuses = helix.sample_status(self.PACID)
            assert statuses is not None

    def test_variants(self, helix):
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "variants.json")) as fp:
            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.POST, 'https://api.staging.helix.com/v0/oauth/access_token',
                    body=LOGIN_BODY, status=200, content_type='application/json')

                rsps.add(
                    responses.POST, 'https://genomics.staging.helix.com/v0/variants/search',
                    body=fp.read(), status=200, content_type='application/json')

                call_set_ids = ["PC-VCIOSK47ERXXIBPO5ZBOMW2HSNCQETCY"]
                variants = helix.variants(call_set_ids)
                assert variants is not None
