import requests

from assetmunki.client import APIClient

from .dto import Asset


class MunkiReportClient(APIClient):
    def __init__(self, base_url, username, password, cookie_name='CSRF-TOKEN'):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._cookie_name = cookie_name
        self.validate()
        self._session = self._authenticate()
    
    def validate(self):
        # TODO: Custom exceptions, better error checking.
        error_str = ''
        missing_str = ''
        if self._base_url is None:
            missing_str += 'base_url;'
        if self._username is None:
            missing_str += 'username;'
        if self._password is None:
            missing_str += 'password;'
        if missing_str != '':
            error_str = f'MunkiReport Client missing: {missing_str}'
            raise Exception(error_str)
        return super().validate()
    
    def query(self, data=[]):
        if data is None or not isinstance(data, list):
            raise ValueError('query data cannot be null & must be a list')
        
        try:
            headers = self._get_request_headers()
            query_data = self._generate_query(data)
            response = self._session.post(self._query_url, data=query_data, headers=headers)
        except Exception as e:
            raise e

        return response.json()
    
    def get_assets(self):
        assets = []
        columns = Asset._columns

        data = self.query(columns)['data']

        for i, d in enumerate(data):
            asset = {}
            for j, c in enumerate(columns):
                key = c.split('.')[1]
                asset[key] = d[j]
            assets.append(asset)
        
        return assets

    @property
    def _auth_url(self):
        return f'{self._base_url}/auth/login'
    
    @property
    def _query_url(self):
        return f'{self._base_url}/datatables/data'

    def _get_request_headers(self):
        return {'x-csrf-token': self._session.cookies[self._cookie_name]}
    
    def _generate_query(self, columns):
        q = {f'columns[{i}][name]': c for i, c in enumerate(columns)}
        return q
    
    def _authenticate(self):
        s = requests.Session()
        r = s.post(self._auth_url, data={
            'login': self._username,
            'password': self._password
        })

        if r.status_code != 200:
            raise Exception('failed to authenticate')

        if not self._cookie_name in s.cookies:
            raise Exception(f'auth did not yield cookie: {self._cookie_name}')

        return s
