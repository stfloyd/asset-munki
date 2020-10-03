import json
import importlib


class Serializeable:
    _attrs = []

    _objs = []

    @classmethod    
    def from_dict(cls, data):
        s = cls()
        for a in s._attrs:
            if not a in data:
                continue
            if a in s._objs:
                if isinstance(s._objs[a], str):
                    # Lazy loading of class type
                    sub_cls = getattr(importlib.import_module(cls.__module__), s._objs[a])
                else:
                    sub_cls = s._objs[a]
                if 'total' in data[a] and 'rows' in data[a]:
                    # Handle nested lists
                    values = []
                    for v in data[a]['rows']:
                        values.append(sub_cls.from_dict(v))
                    setattr(s, a, values)
                else:
                    setattr(s, a, sub_cls.from_dict(data[a]))
            else:
                setattr(s, a, data[a])
        return s
    
    @classmethod
    def from_json(cls, data):
        return cls.from_dict(json.dumps(data))

    def to_dict(self):
        data = {}
        for a in self._attrs:
            if a in self._objs:
                data[a] = getattr(self, a).to_dict()
            else:
                data[a] = getattr(self, a)
        return data
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def __repr__(self):
        return f'<Serializeable>'


class SerializeMapper(object):
    """
    WIP:
    Maps keys & values between Serializeable types.
    """
    def __init__(self, *args):
        super().__init__()
        self.integrations = args
        self.mappings = []

    def define_mapping(self, *args):
        self.mappings.append(*args)