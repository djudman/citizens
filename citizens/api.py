import functools
import numpy as np
from datetime import datetime
from itertools import groupby

from aiohttp import web
from aiojobs.aiohttp import atomic

from citizens.data import DataValidationError, CitizenValidator, validate_import_data
from citizens.storage import CitizenNotFoundError


class CitizensApiError(Exception):
    pass


@atomic
async def new_import(request):
    logger = request.app.logger
    import_data = await request.json()
    if 'citizens' not in import_data:
        raise DataValidationError('Key `citizens` not found.')
    citizens = import_data['citizens']
    storage = request.app.storage
    validate_import_data(citizens)
    import_id = await storage.generate_import_id() # TODO: тут всё ещё есть проблема
    await storage.new_import(import_id, citizens)
    out = {'data': {'import_id': import_id}}
    logger.debug(f'Data imported (import_id = {import_id})')
    return web.json_response(data=out, status=201)


@atomic
async def update_citizen(request):
    import_id = int(request.match_info['import_id'])
    citizen_id = int(request.match_info['citizen_id'])
    citizen_data = await request.json()
    if 'citizen_id' in citizen_data:
        raise DataValidationError('Forbidden to update field `citizen_id`.')
    CitizenValidator().validate(citizen_data, all_fields_required=False)
    try:
        if 'relatives' in citizen_data:
            for relative_id in citizen_data['relatives']:
                await request.app.storage.get_one_citizen(
                    import_id, relative_id, return_fields=['citizen_id'])
        updated_data = await request.app.storage.update_citizen(
            import_id, citizen_id, citizen_data)
    except CitizenNotFoundError as e:
        raise DataValidationError('You try to set non existent citizens.') from e
    return web.json_response(data={'data': updated_data})


async def get_citizens(request):
    import_id = int(request.match_info['import_id'])
    citizens = [data async for data in request.app.storage.get_citizens(import_id)]
    return web.json_response(data={'data': citizens})


async def get_presents_by_month(request):
    import_id = int(request.match_info['import_id'])
    report = await request.app.storage.get_presents_by_month(import_id)
    presents_by_month = {entry['month']: entry['citizens'] for entry in report}
    for month in range(1, 13):
        if month not in presents_by_month:
            presents_by_month[month] = []
    return web.json_response(data={'data': presents_by_month})


async def get_age_percentiles(request):
    import_id = int(request.match_info['import_id'])
    report = await request.app.storage.get_ages_by_town(import_id)
    percentile = functools.partial(np.percentile, interpolation='linear')
    age_percentiles = [
        {
            'town': entry['town'],
            'p50': round(percentile(entry['ages'], 50), 2),
            'p75': round(percentile(entry['ages'], 75), 2),
            'p99': round(percentile(entry['ages'], 99), 2),
        } for entry in report
    ]
    return web.json_response(data={'data': age_percentiles})
