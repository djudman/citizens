import math
import numpy as np
from datetime import datetime
from itertools import groupby

from aiohttp import web

from citizens.data import (
    validate_import_data, validate_citizen_data, DataValidationError
)


class CitizensApiError(Exception):
    pass


async def new_import(request):
    import_data = await request.json()
    try:
        validate_import_data(import_data)
    except DataValidationError as e:
        # TODO: логировать ошибки в файл
        return web.Response(status=400)
    import_id = request.app.storage.new_import(import_data)
    out = {'data': {'import_id': import_id}}
    return web.json_response(data=out, status=201)


async def update_citizen(request):
    import_id = int(request.match_info['import_id'])
    citizen_id = int(request.match_info['citizen_id'])
    citizen_data = await request.json()
    try:
        if 'citizen_id' in citizen_data:
            raise DataValidationError('citizen_id cannot be updated')
        citizen_data['citizen_id'] = citizen_id
        new_data = validate_citizen_data(citizen_data, all_fields_required=False)
    except DataValidationError:
        # TODO: логировать ошибки в файл
        return web.Response(status=400)

    try:
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
    except CitizensApiError:
        # TODO: inconsistent relatives
        return web.Response(status=400)

    updated_data = request.app.storage.update_citizen(import_id, citizen_id, new_data)
    return web.json_response(data={'data': updated_data})


def get_citizens(request):
    import_id = int(request.match_info['import_id'])
    citizens = request.app.storage.get_citizens(import_id)
    return web.json_response(data={'data': citizens})


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
    return web.json_response(data={'data': presents_by_month})


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
    return web.json_response(data={'data': age_percentiles})


def get_one_citizen(storage, import_id, citizen_id):
    citizens = storage.get_citizens(import_id, {'citizen_id': citizen_id})
    if len(citizens) == 1:
        return citizens[0]
    raise CitizensApiError('Expected 1 entry. Got {0}'.format(len(citizens)))
