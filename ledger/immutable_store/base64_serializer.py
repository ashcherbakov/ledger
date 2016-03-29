import base64
import json
from typing import Dict

from ledger.immutable_store.mappingserializer import MappingSerializer


# Consider using bson or ubjson for serializing json


class OrderedJsonEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        kwargs["ensure_ascii"] = False
        kwargs["sort_keys"] = True
        super().__init__(*args, *kwargs)

    def encode(self, o):
        if isinstance(o, bytes) or isinstance(o, bytearray):
            return '"{}"'.format(base64.b64encode(o).decode("utf-8"))
        elif isinstance(o, dict):
            return "{" + ",".join([self.encode(k)+":"+self.encode(v)
                                   for (k, v) in o.items()]) + "}"
        else:
            return json.JSONEncoder.encode(self, o)


class Base64Serializer(MappingSerializer):
    jsonEncoder = OrderedJsonEncoder()

    def serialize(self, data: Dict, fields=None, toBytes=True):
        encoded = self.jsonEncoder.encode(data)
        if toBytes:
            encoded = encoded.encode()
        return encoded

    def deserialize(self, data):
        return json.loads(data)
