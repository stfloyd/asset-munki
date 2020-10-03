import json
import importlib

from assetmunki.interop import Serializeable


class Asset(Serializeable):
    _columns = [
        'machine.serial_number',
        'machine.machine_name',
        'machine.machine_model',
        'machine.machine_desc',
        'machine.hostname',
        'reportdata.long_username',
        'reportdata.console_user',
        'machine.os_version',
        'machine.buildversion',
        'machine.cpu',
        'machine.physical_memory',
        'warranty.purchase_date',
        'warranty.end_date',
        'warranty.status',
        'munkireport.manifestname',
        'diskreport.totalsize',
        'diskreport.volumetype',
        'diskreport.media_type'
    ]

    _attrs = [
        'serial_number',
        'machine_name',
        'machine_model',
        'machine_desc',
        'hostname',
        'long_username',
        'console_user',
        'os_version',
        'buildversion',
        'cpu',
        'physical_memory',
        'purchase_date',
        'end_date',
        'manifestname',
        'totalsize'
    ]
