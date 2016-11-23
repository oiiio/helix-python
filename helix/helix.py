import json
from enum import Enum

import logging
import requests
from pendulum import Pendulum
from requests.auth import HTTPBasicAuth

from .schemas import EventSchema, CustomerInfoSchema, SampleStatusSchema, VariantSchema


class EventTypes(Enum):
    sampleStatusUpdate = 1
    accountUpdate = 2
    accessRevoked = 3


class Scope:
    IDENTITY = "identity"
    GENOMICS = "genomics"


class Helix:
    def __init__(self, staging=False, **kwargs):
        self.expires = Pendulum.now()
        self.scope = Scope.IDENTITY
        self.session = None
        self.is_staging = staging
        self.grant_type = kwargs.get('grant_type', "client_credentials")
        self.client_id = kwargs.get('client_id', None)
        self.client_secret = kwargs.get('client_secret', None)
        self.genomic_client_id = kwargs.get('genomic_client_id', None)
        self.genomic_client_secret = kwargs.get('genomic_client_secret', None)

    @property
    def url(self):
        if self.is_staging:
            return "https://{}.{}helix.com/v0".format(
                "api" if self.scope != Scope.GENOMICS else "genomics",
                "staging." if self.is_staging else ''
            )

    def login(self, scope=Scope.IDENTITY):
        if scope:
            if scope not in [Scope.IDENTITY, Scope.GENOMICS]:
                raise ValueError("Invalid scope: {}".format(self.scope))
            self.scope = scope

        if self.scope == Scope.IDENTITY:
            if self.client_id is None or self.client_secret is None:
                raise ValueError("Must supply a client_id and client_secret to log in.")
            client_id = self.client_id
            client_secret = self.client_secret
        else:
            if self.genomic_client_id is None or self.genomic_client_secret is None:
                raise ValueError("Must supply a genomic_client_id and genomic_client_secret to __init__.")
            client_id = self.genomic_client_id
            client_secret = self.genomic_client_secret

        creds = {
            'grant_type': self.grant_type,
            'scope': scope
        }
        auth_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.session = requests.Session()

        # login
        # NOTE: AUTH is always against api..helix.com
        _scope = self.scope
        self.scope = Scope.IDENTITY

        r = requests.post(self.url + '/oauth/access_token', auth=HTTPBasicAuth(client_id, client_secret), data=creds,
                          headers=auth_headers)

        # put it back to the correct scope
        self.scope = _scope

        r.raise_for_status()
        data = r.json()

        # setup expires...
        dt = Pendulum.now()
        self.expires = dt.add(data["expires_in"])

        self.session.headers.update({
            'Authorization': data["token_type"] + " " + data["access_token"],
            'Content-type': 'application/json',
        })
        return data

    def _refresh_if_expired(self, scope=Scope.IDENTITY):
        if scope != self.scope:
            self.login(scope=scope)
            return
        if Pendulum.now() > self.expires:
            self.login(self.scope)

    def _get(self, url, payload=None):
        rv = self.session.get(self.url + url, params=payload)
        logging.info("{} GET {}".format(rv.status_code, rv.url))
        rv.raise_for_status()
        return rv.json()

    def _post(self, url, payload=None):
        rv = self.session.post(self.url + url, data=json.dumps(payload))
        logging.info("{} POST {}".format(rv.status_code, rv.url))
        rv.raise_for_status()
        try:
            rv = rv.json()
        except:
            pass
        return rv

    def _put(self, url, payload=None):
        rv = self.session.put(self.url + url, data=json.dumps(payload))
        logging.info("{} PUT {}".format(rv.status_code, rv.url))
        rv.raise_for_status()
        try:
            rv = rv.json()
        except:
            pass
        return rv

    def _delete(self, url):
        rv = self.session.delete(self.url + url)
        logging.info("{} DEL {}".format(rv.status_code, rv.url))
        rv.raise_for_status()

    def events(self, after=0, limit=100, event_type=None):
        """
        Fetch events starting at `after` and limited to `limit` number of events.

        :param after: The event to start after.
        :param limit: Max number of events to fetch.
        :param event_type: Type of events to fetch.  Must be one of sampleStatusUpdate, accountUpdate, accessRevoked.
        :return: List of event dictionaries.
        """
        self._refresh_if_expired()
        query_params = {
            'after': after,
            'limit': limit
        }

        if event_type:
            if event_type not in EventTypes:
                raise ValueError("Bad event type.  Must be one of {}".format(str(EventTypes)))
            query_params['eventType'] = event_type.name

        data = self._get('/events', payload=query_params)
        rv = []
        for event in data["events"]:
            rv.append(EventSchema(strict=True).load(event).data)
        return rv

    def customer_info(self, pacid):
        """
        Get customer's information.

        :param pacid: the pacId, Partner app customerID, associated with a specific user
        :return: Customer information dictionary
        """
        self._refresh_if_expired()
        data = self._get('/customers/{}'.format(pacid))
        return CustomerInfoSchema(strict=True).load(data).data

    def sample_status(self, pacid):
        """
        Get the customer's sample status.
        :param pacid: partner-application-customer ID
        :return: An array of sample status messages.
        """
        self._refresh_if_expired()
        data = self._get('/customers/{}/samplestatus'.format(pacid))
        rv = []
        for status in data["sampleStatus"]:
            rv.append(SampleStatusSchema(strict=True).load(status).data)
        return rv

    def variants(self, call_set_ids=()):
        """
        Fetch genomic information on the customer using the list of call_set_ids.

        :param call_set_ids: Array of call set ids.
        :return: Genomic information.
        """
        if not call_set_ids:
            raise ValueError("Variant search requires at least one callSetId")
        self._refresh_if_expired(scope=Scope.GENOMICS)

        data = {
            'callSetIds': call_set_ids
        }
        data = self._post('/variants/search', payload=data)

        rv = []
        for variant in data:
            rv.append(VariantSchema(strict=True).load(variant).data)
        return rv
