import json
from datetime import datetime

from aiohttp import web


class CitizensApiError(Exception):
    pass


class InvalidImportData(CitizensApiError):
    pass


def verify_citizen(data):
    cid = citizen.get('citizen_id', '<no value>')  # Используется в сообщениях об ошибках
    # NOTE: тут можно было бы использовать dataclass
    fields = {('citizen_id', int), ('town', str), ('street', str),
              ('building', str), ('apartment', int), ('name', str),
              ('birth_date', str), ('gender', str), ('relatives', list)}
    for field, field_type in fields:
        if field not in citizen:
            raise InvalidImportData(f'Citizen `{cid}` has no field `{name}`')
        value = citizen[field]
        if not isinstance(value, field_type):
            expected_type = field_type.__name__
            real_type = type(value).__name__
            err = f'Citizen `{cid}` has invalid type for field `{field}`. '
                  f'Expected `{type_name}`, got `{real_type}`)'
            raise InvalidImportData(err)
    try:
        datetime.strptime(data['birth_date'])
    except ValueError as e:
        err = f'Invalid format of `birth_date` for citizen `{cid}`'
        raise InvalidImportData(err) from e
    return cid


def verify_import(data):
    relatives_map = {}
    for citizen_data in data:
        cid = verify_citizen(citizen_data)
        relatives_map[cid] = citizen_data['relatives']
    for cid, relatives in relatives_map.items():
        for relative_cid in relatives:
            if cid not in relatives_map[relative_cid]:
                raise InvalidImportData(f'Invalid relatives for `{cid}`')


async def new_import(request):
    import_data = await request.json()
    try:
        verify_import(import_data)
    except CitizensApiError:
        # TODO: логировать ошибки в файл
        return web.Response(status=400)
    import_id = request.app.storage.new_import(import_data)
    out = {'data': {'import_id': import_id}}
    return web.Response(body=json.dumps(out), status=201)
