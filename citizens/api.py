import asyncio
import functools
import math
import numpy as np
from datetime import datetime
from itertools import groupby

from aiohttp import web

from citizens.data import DataValidationError, CitizenValidator, validate_import_data
from citizens.storage import CitizenNotFoundError


class CitizensApiError(Exception):
    pass


async def new_import(request):
    import_data = await asyncio.shield(request.json())
    storage = request.app.storage
    validate_import_data(import_data)
    import_id = await storage.generate_import_id() # TODO: тут всё ещё есть проблема
    await storage.new_import(import_id, import_data)
    out = {'data': {'import_id': import_id}}
    return web.json_response(data=out, status=201)


async def update_citizen(request):
    import_id = int(request.match_info['import_id'])
    citizen_id = int(request.match_info['citizen_id'])
    citizen_data = await asyncio.shield(request.json())
    if 'citizen_id' in citizen_data:
        raise DataValidationError('Forbidden to update field `citizen_id`.')
    CitizenValidator().validate(citizen_data, all_fields_required=False)
    try:
        if 'relatives' in citizen_data:
            for relative_id in citizen_data['relatives']:
                await request.app.storage.get_one_citizen(import_id, relative_id)  # TODO: тут можно выбрать только _id.
        updated_data = await request.app.storage.update_citizen(import_id, citizen_id, citizen_data)
    except CitizenNotFoundError as e:
        raise DataValidationError('You try to set non existent citizens.') from e
    return web.json_response(data={'data': updated_data})


async def get_citizens(request):
    import_id = int(request.match_info['import_id'])
    citizens = [data async for data in request.app.storage.get_citizens(import_id)]
    return web.json_response(data={'data': citizens})


async def get_presents_by_month(request):
    import_id = int(request.match_info['import_id'])
    citizens = request.app.storage.get_citizens(import_id)
    presents_by_month = {month: [] for month in range(1, 13)}
    async for citizen in citizens:
        relatives_birthdays = []
        for cid in citizen['relatives']:
            relative_data = await request.app.storage.get_one_citizen(import_id, cid)
            dt = datetime.strptime(relative_data['birth_date'], '%d.%m.%Y')
            relatives_birthdays.append(dt)
        citizen_id = citizen['citizen_id']
        for month, dates in groupby(relatives_birthdays, key=lambda date: date.month):
            presents_by_month[month].append({
                'citizen_id': citizen_id,
                'presents': len(list(dates)),
            })
    return web.json_response(data={'data': presents_by_month})


async def get_age_percentiles(request):
    import_id = int(request.match_info['import_id'])
    citizens = [data async for data in request.app.storage.get_citizens(import_id)]
    age_percentiles = []
    percentile = functools.partial(np.percentile, interpolation='linear')
    for town, citizens_in_town in groupby(citizens, key=lambda data: data['town']):
        ages = []
        for citizen in citizens_in_town:
            birth_dt = datetime.strptime(citizen['birth_date'], '%d.%m.%Y')
            age = datetime.now().year - birth_dt.year
            ages.append(age)
        age_percentiles.append({
            'town': town,
            'p50': round(percentile(ages, 50), 2),
            'p75': round(percentile(ages, 75), 2),
            'p99': round(percentile(ages, 99), 2),
        })
    return web.json_response(data={'data': age_percentiles})
