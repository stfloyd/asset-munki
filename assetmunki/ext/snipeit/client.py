import json
import requests
import time
import logging

from assetmunki.client import APIClient
from .exceptions import SnipeITAssetNotFoundError
from . import dto


class SnipeITClient(APIClient):
    def __init__(self, base_url, token):
        self._base_url = base_url
        self._token = token
        self.validate()
    
    def validate(self):
        # TODO: Custom exceptions, better error checking.
        missing_str = ''
        if self._base_url is None:
            missing_str += 'base_url;'
        if self._token is None:
            missing_str += 'token;'
        if missing_str != '':
            error_str = f'SnipeIT Client missing: {missing_str}'
            raise Exception(error_str)
        return super().validate()
    
    def request(self, method, endpoint, data=None, params=None):
        headers = self._get_request_headers()
        url = self._base_url + endpoint
        response = requests.request(method, url, headers=headers, data=data, params=params)
        response_json = json.loads(response.content)
        if 'messages' in response_json and response_json['messages'] == 429:
            logging.info('Too many requests, sleeping for 30 seconds.')
            time.sleep(30)
            return self.request(method, endpoint, data)
        return response
    
    def get(self, endpoint, params=None):
        data = []
        response = self.request('GET', endpoint, params=params)
        try:
            response_json = json.loads(response.content)
            return response_json['rows']
        except Exception as e:
            logging.error(f'Ran into an error parsing: {json.loads(response.content)}')
            logging.exception(e)
            return response

    def get_dto(self, dto_cls):
        if dto_cls._url_relative is None:
            return None
        data = []
        payload = self.get(dto_cls._url_relative)
        for raw in payload:
            data.append(dto_cls.from_dict(raw))
        return data
    
    def post_dto(self, data, dto_cls):
        if dto_cls._url_relative is None:
            return None
        if (isinstance(data, dto_cls)):
            response = self.request('POST', dto_cls._url_relative, data=data.to_json())
        elif (isinstance(data, dict)):
            response = self.request('POST', dto_cls._url_relative, data=json.dumps(data))
        else:
            response = self.request('POST', dto_cls._url_relative, data=data)
        return json.loads(response.content.decode('utf-8'))
    
    def update_dto(self, id, data, dto_cls):
        if dto_cls._url_relative is None:
            return None
        if (isinstance(data, dto_cls)):
            response = self.request('PUT', f'{dto_cls._url_relative}/{id}', data=data.to_json())
        elif (isinstance(data, dict)):
            response = self.request('PUT', f'{dto_cls._url_relative}/{id}', data=json.dumps(data))
        else:
            response = self.request('PUT', f'{dto_cls._url_relative}/{id}', data=data)
        return json.loads(response.content.decode('utf-8'))

    def get_users(self):
        return self.get_dto(dto.User)
    
    def get_models(self):
        return self.get_dto(dto.Model)
    
    def get_categories(self):
        return self.get_dto(dto.AssetCategory)
    
    def get_manufacturers(self):
        return self.get_dto(dto.Manufacturer)
    
    def get_fields(self):
        return self.get_dto(dto.Field)
    
    def get_fieldsets(self):
        return self.get_dto(dto.FieldSet)
    
    def get_hardware(self):
        return self.get_dto(dto.Asset)
    
    def get_companies(self):
        return self.get_dto(dto.Company)
    
    def post_model(self, model_dto):
        return self.post_dto(model_dto, dto.Model)

    def update_model(self, id, model_dto):
        return self.update_dto(id, model_dto, dto.Model)
    
    def post_asset(self, model_dto):
        return self.post_dto(model_dto, dto.Asset)
    
    def update_asset(self, id, model_dto):
        return self.update_dto(id, model_dto, dto.Asset)
    
    def search_user(self, search_str):
        return self.get('/users', params={
            'limit': 50,
            'offset': 0,
            'search': search_str
        })

    def get_model(self, model_id):
        models = self.get_models()
        for m in models:
            if m.id == model_id:
                return m
        return None
    
    def model_exists(self, model_number):
        exists = False
        for model in self.get_models():
            if model_number == model.model_number:
                exists = True
                break
        return exists
    
    def get_model_id(self, model_number):
        existing_id = None
        for model in self.get_models():
            if model_number == model.model_number:
                existing_id = model.id
                break
        return existing_id
    
    def get_asset_by_serial(self, serial):
        try:
            response = self.request('GET', f'/hardware/byserial/{serial}')
            response_json = json.loads(response.content.decode('utf-8'))
            if response_json['total'] > 1:
                payload = response_json['rows'][-1]
            else:
                payload = response_json['rows'][0]
            return dto.Asset.from_dict(payload)
        except Exception as e:
            raise SnipeITAssetNotFoundError(f'Could not find hardware with serial: {serial}') from e
    
    def payload_from_mr(data, mr_data, is_new=True):
        pass

    def _get_request_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._token}'
        }
