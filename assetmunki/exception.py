class ErrorFormatter:
    @staticmethod
    def type_error(expected, provided):
        return f'Invalid type, expected {str(expected)} but got {str(provided)}'


class AssetMunkiError(Exception):
    def __init__(self, message, assetmunki=None, *args, **kwargs):
        super().__init__(message)
        self.assetmunki = assetmunki


class InitializationError(AssetMunkiError):
    pass


class IntegrationError(AssetMunkiError):
    def __init__(self, message, assetmunki=None, integration=None, *args, **kwargs):
        super().__init__(message, assetmunki, *args, **kwargs)
        self.integration = integration


class InvalidIntegrationError(IntegrationError):
    pass


class IntegrationInitializationError(IntegrationError):
    def __init__(self, message, assetmunki=None, integration=None, *args, **kwargs):
        super().__init__(message, assetmunki, integration, *args, **kwargs)


class IntegrationTypeError(InvalidIntegrationError):
    pass


class UnauthorizedIntegrationError(IntegrationError):
    pass


class IntegrationRegistrationError(IntegrationInitializationError):
    pass


class DuplicateIntegrationError(IntegrationRegistrationError):
    pass
