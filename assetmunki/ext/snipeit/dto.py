from assetmunki.interop import Serializeable


class User(Serializeable):
    _url_relative = '/users'

    _attrs = [
        'id', 'first_name', 'last_name', 'username',
        'email', 'phone', 'website', 'address', 'city',
        'state', 'country', 'zip', 'company', 'manager',
        'jobtitle', 'employee_num', 'department', 'location',
        'notes'
    ]

    _objs = {
        'company': 'Company',
        'department': 'Department',
        'location': 'Location'
    }

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class Company(Serializeable):
    _url_relative = '/companies'

    _attrs = [
        'name'
    ]

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class Department(Serializeable):
    _attrs = [
        'name'
    ]

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class Location(Serializeable):
    _url_relative = '/locations'

    _attrs = [
        'name'
    ]

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class Asset(Serializeable):
    _url_relative = '/hardware'

    _attrs = [
        'id', 'asset_tag', 'name', 'company', 'model',
        'serial', 'assigned_to'
    ]

    _objs = {
        'company': 'Company',
        'model': 'Model'
    }

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.company} - {self.asset_tag} - {self.model}>'


class Model(Serializeable):
    _url_relative = '/models'

    _attrs = [
        'id', 'name', 'manufacturer',
        'image', 'model_number',
        'category'
    ]

    _objs = {
        'manufacturer': 'Manufacturer',
        'category': 'AssetCategory'
    }

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class Manufacturer(Serializeable):
    _url_relative = '/manufacturers'

    _attrs = [
        'id', 'name'
    ]

    def __repr__(self):
        return f'<Manufacturer {self.name}>'


class AssetCategory(Serializeable):
    _url_relative = '/categories'

    _attrs = [
        'id', 'name'
    ]

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class FieldSet(Serializeable):
    _url_relative = '/fieldsets'

    _attrs = [
        'id', 'name', 'fields'
    ]

    _objs = {
        'fields': 'Field'
    }

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class Field(Serializeable):
    _url_relative = '/fields'

    _attrs = [
        'id', 'name', 'db_column_name'
    ]

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'
