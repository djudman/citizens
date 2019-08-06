import json
import math
import numpy as np
from datetime import datetime
from itertools import groupby

from aiohttp import web


class CitizensApiError(Exception):
    pass


class InvalidImportData(CitizensApiError):
    pass


def verify_citizen(data):
    cid = data.get('citizen_id', '<no value>')  # Используется в сообщениях об ошибках
    # NOTE: тут можно было бы использовать dataclass
    fields = {('citizen_id', int), ('town', str), ('street', str),
              ('building', str), ('apartment', int), ('name', str),
              ('birth_date', str), ('gender', str), ('relatives', list)}
    for field, field_type in fields:
        if field not in data:
            raise InvalidImportData(f'Citizen `{cid}` has no field `{field}`')
        value = data[field]
        if not isinstance(value, field_type):
            expected_type = field_type.__name__
            real_type = type(value).__name__
            err = f'Citizen `{cid}` has invalid type for field `{field}`. '\
                  f'Expected `{expected_type}`, got `{real_type}`)'
            raise InvalidImportData(err)
    try:
        datetime.strptime(data['birth_date'], '%d.%m.%Y')
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
    return web.Response(content_type='application/json', body=json.dumps(out),
                        status=201)


def get_one_citizen(storage, import_id, citizen_id):
    citizens = storage.get_citizens(import_id, {'citizen_id': citizen_id})
    assert len(citizens) == 1
    return citizens[0]


async def update_citizen(request):
    import_id = int(request.match_info['import_id'])
    citizen_id = int(request.match_info['citizen_id'])
    citizen_data = await request.json()
    if not citizen_data:
        raise CitizensApiError('No citizen data')
    if 'citizen_id' in citizen_data:
        raise CitizensApiError('Field `citizen_id` is not allowed to change')
    editable_fields = {'name', 'gender', 'birth_date', 'relatives', 'town',
        'street', 'building', 'apartment'}
    new_data = {field: citizen_data[field] for field in editable_fields if field in citizen_data}

    # TODO: проверить корректность birth_date, если задано
    if 'relatives' in citizen_data:
        old_data = get_one_citizen(request.app.storage, import_id, citizen_id)
        old_relatives = old_data['relatives']
        received_relatives = citizen_data['relatives']
        for cid in old_relatives:
            if cid not in received_relatives:
                # NOTE: Удаляем на той стороне меня из relatives
                data = get_one_citizen(request.app.storage, import_id, cid)
                if citizen_id in data['relatives']:
                    data['relatives'].remove(citizen_id)
                request.app.storage.update_citizen(import_id, cid, {'relatives': data['relatives']})
        for cid in received_relatives:
            if cid not in old_relatives:
                # NOTE: Добавляем на той стороне меня в relatives
                data = get_one_citizen(request.app.storage, import_id, cid)
                if citizen_id not in data['relatives']:
                    data['relatives'].append(citizen_id)
                request.app.storage.update_citizen(import_id, cid, {'relatives': data['relatives']})

    updated_data = request.app.storage.update_citizen(import_id, citizen_id, new_data)
    return web.Response(content_type='application/json', body=json.dumps(updated_data))


def get_citizens(request):
    import_id = int(request.match_info['import_id'])
    citizens = request.app.storage.get_citizens(import_id)
    return web.Response(content_type='application/json', body=json.dumps(citizens))


def get_presents_by_month(request):
    import_id = int(request.match_info['import_id'])
    citizens = request.app.storage.get_citizens(import_id)
    presents_by_month = {month: [] for month in range(1, 13)}
    for citizen in citizens:
        relatives_birthdays = []
        for cid in citizen['relatives']:
            relative_data = get_one_citizen(request.app.storage, import_id, cid)
            dt = datetime.strptime(relative_data['birth_date'], '%d.%m.%Y')
            relatives_birthdays.append(dt)
        for month, dates in groupby(relatives_birthdays, key=lambda date: date.month):
            presents_by_month[month].append({
                'citizen_id': citizen['citizen_id'],
                'presents': len(list(dates)),
            })
    out = {'data': presents_by_month}
    return web.Response(content_type='application/json', body=json.dumps(out))


def get_age_percentiles(request):
    import_id = int(request.match_info['import_id'])
    citizens = request.app.storage.get_citizens(import_id)
    age_percentiles = []
    for town, citizens_in_town in groupby(citizens, key=lambda data: data['town']):
        ages = []
        for citizen in citizens_in_town:
            birth_dt = datetime.strptime(citizen['birth_date'], '%d.%m.%Y')
            delta = datetime.now() - birth_dt
            age = math.floor(delta.days / 365)
            ages.append(age)
        age_percentiles.append({
            'town': town,
            'p50': math.floor(np.percentile(ages, 50, interpolation='linear')),
            'p75': math.floor(np.percentile(ages, 75, interpolation='linear')),
            'p99': math.floor(np.percentile(ages, 99, interpolation='linear')),
        })
    out = {'data': age_percentiles}
    return web.Response(content_type='application/json', body=json.dumps(out))
