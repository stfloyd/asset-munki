import os

from assetmunki.integration import Integration
from assetmunki.exception import (
    IntegrationInitializationError,
    InvalidIntegrationError
)

from .client import SnipeITClient


class SnipeIntegration(Integration):
    name = 'snipeit'

    def __init__(self, assetmunki=None):
        self.api_url = self._get_config_value('SNIPEIT_URL', assetmunki)
        self.api_token = self._get_config_value('SNIPEIT_TOKEN', assetmunki)
        self.client = None
        super().__init__(assetmunki)

    def init_assetmunki(self, assetmunki):
        try:
            self.client = SnipeITClient(self.api_url, self.api_token)
        except Exception as e:
            msg = f'Failed to initialize SnipeIT API client, "{self.name}" integration initialization failed'
            raise IntegrationInitializationError(msg, assetmunki, self) from e
        super().init_assetmunki(assetmunki)
        assetmunki.config['SNIPEIT_URL'] = self.api_url
        assetmunki.config['SNIPEIT_TOKEN'] = self.api_token
    
    def check_valid(self, assetmunki):
        if self.api_url is None:
            raise InvalidIntegrationError('Invalid Integration: missing API URL', assetmunki, self)
        if self.api_token is None:
            raise InvalidIntegrationError('Invalid Integration: missing API token', assetmunki, self)
        return super().check_valid(assetmunki)