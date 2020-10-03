import os

from assetmunki.integration import Integration
from assetmunki.exception import (
    IntegrationInitializationError,
    InvalidIntegrationError
)

from .client import MunkiReportClient


class MunkiReportIntegration(Integration):
    name = 'munkireport'

    def __init__(self, assetmunki=None):
        self.api_url = self._get_config_value('MUNKIREPORT_URL', assetmunki)
        self.api_username = self._get_config_value('MUNKIREPORT_USERNAME', assetmunki)
        self.api_password = self._get_config_value('MUNKIREPORT_PASSWORD', assetmunki)
        self.client = None
        super().__init__(assetmunki)

    def init_assetmunki(self, assetmunki):
        try:
            self.client = MunkiReportClient(self.api_url,
                                            self.api_username,
                                            self.api_password)
        except Exception as e:
            msg = f'Failed to initialize MunkiReport API client, "{self.name}" integration initialization failed'
            raise IntegrationInitializationError(msg, assetmunki, self) from e
        super().init_assetmunki(assetmunki)
        assetmunki.config['MUNKIREPORT_URL'] = self.api_url
        assetmunki.config['MUNKIREPORT_USERNAME'] = self.api_username
        assetmunki.config['MUNKIREPORT_PASSWORD'] = self.api_password
    
    def check_valid(self, assetmunki):
        if self.api_url is None:
            raise InvalidIntegrationError('Invalid Integration: missing API URL', assetmunki, self)
        if self.api_username is None:
            raise InvalidIntegrationError('Invalid Integration: missing API username', assetmunki, self)
        if self.api_password is None:
            raise InvalidIntegrationError('Invalid Integration: missing API password', assetmunki, self)
        return super().check_valid(assetmunki)