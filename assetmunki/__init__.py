""" Asset Munki core utility class """


current_instance = None


class AssetMunki(object):
    def __init__(self):
        current_instance = self
        self.integrations = {}
        self.config = {}

