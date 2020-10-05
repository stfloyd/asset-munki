import os

from . import AssetMunki
from .exception import (
    ErrorFormatter,
    IntegrationError,
    IntegrationInitializationError,
    InvalidIntegrationError,
    IntegrationTypeError,
    DuplicateIntegrationError
)


class Integration(object):
    name = None

    def __init__(self, assetmunki=None):
        if assetmunki is not None:
            try:
                self.init_assetmunki(assetmunki)
            except IntegrationError as e:
                msg = f'Failed to initialize "{self.name}" integration with AssetMunki'
                e2 = IntegrationInitializationError(msg, assetmunki)
                raise e2 from e

    def init_assetmunki(self, assetmunki):
        self.check_valid(assetmunki)
        assetmunki.integrations[self.name] = self
        self.assetmunki = assetmunki

    def check_valid(self, assetmunki):
        if not isinstance(assetmunki, AssetMunki):
            msg = ErrorFormatter.type_error(AssetMunki, type(assetmunki))
            raise IntegrationTypeError(msg, assetmunki, self)
        if self.name is None:
            msg = 'Invalid Integration: no name provided'
            raise InvalidIntegrationError(msg, assetmunki, self)
        if self.name in assetmunki.integrations:
            msg = f'Integration with name "{self.name}" already registered'
            raise DuplicateIntegrationError(msg, assetmunki, self)

    def _get_config_value(self, key, assetmunki=None, failover=None):
        if assetmunki is None:
            return os.getenv(key, failover)
        return assetmunki.config.get(key, os.getenv(key, failover))