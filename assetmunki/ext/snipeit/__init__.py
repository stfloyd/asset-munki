import os

from assetmunki.integration import Integration
from assetmunki.exception import (
    IntegrationInitializationError,
    InvalidIntegrationError
)

from .client import SnipeITClient
from .dto import Manufacturer, AssetCategory


class SnipeIntegration(Integration):
    name = 'snipeit'

    def __init__(self, assetmunki=None):
        self.api_url = self._get_config_value('SNIPEIT_URL', assetmunki)
        self.api_token = self._get_config_value('SNIPEIT_TOKEN', assetmunki)
        self.client = None
        self.manufacturer = None
        self.categories = {}
        self.fieldsets = {}
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
        self.validate_or_populate_companies()
        self.validate_or_populate_categories()
        self.validate_or_populate_fieldsets()
    
    def validate_or_populate_fieldsets(self):
        if self.client is None:
            raise InvalidIntegrationError('Invalid Integration: invalid client', self.assetmunki, self)

        fieldsets = self.client.get_fieldsets()

    def validate_or_populate_categories(self):
        if self.client is None:
            raise InvalidIntegrationError('Invalid Integration: invalid client', self.assetmunki, self)

        categories = self.client.get_categories()

        for c in categories:
            if c.name.lower() in ['laptops', 'desktops', 'unknown']:
                self.categories[c.name.lower()] = c
        
        if 'laptops' not in self.categories:
            # create laptops category
            self.categories['laptops'] = self.client.post_dto({
                'name': 'Laptops'
            }, AssetCategory)
        if 'desktops' not in self.categories:
            # create desktops category
            self.categories['desktops'] = self.client.post_dto({
                'name': 'Desktops'
            }, AssetCategory)
        if 'unknown' not in self.categories:
            # create unknown category
            self.categories['unknown'] = self.client.post_dto({
                'name': 'Unknown'
            }, AssetCategory)
        
        return True

    def validate_or_populate_manufacturers(self):
        if self.client is None:
            raise InvalidIntegrationError('Invalid Integration: invalid client', self.assetmunki, self)

        manufacturers = self.client.get_manufacturers()

        found = False

        for m in manufacturers:
            if m.name == 'Apple':
                self.manufacturer = m
                return True
        
        if found:
            return True
        else:
            self.manufacturer = self.client.post_dto({
                'name': 'Apple'
            }, Manufacturer)
    
    def check_valid(self, assetmunki):
        if self.api_url is None:
            raise InvalidIntegrationError('Invalid Integration: missing API URL', assetmunki, self)
        if self.api_token is None:
            raise InvalidIntegrationError('Invalid Integration: missing API token', assetmunki, self)

        # Make sure we have categories we need
        return super().check_valid(assetmunki)