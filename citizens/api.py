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
    validate_import_data(citizens)
    import_id = await request.app.storage.import_citizens(citizens)
    out = {'data': {'import_id': import_id}}
    logger.debug(f'Data imported (import_id = {import_id})')
    return web.json_response(data=out, status=201)


@atomic
async def update_citizen(request):
    import_id = int(request.match_info['import_id'])
    citizen_id = int(request.match_info['citizen_id'])
    values = await request.json()
    if not values:
        raise DataValidationError('No values.')
    if 'citizen_id' in values:
        raise DataValidationError('Forbidden to update field `citizen_id`.')
    CitizenValidator().validate(values, all_fields_required=False)
    storage = request.app.storage
    try:
        if 'relatives' in values:
            relatives = list(await storage.get_citizens(
                import_id,
                filter={'citizen_id': values['relatives']},
                return_fields=['citizen_id']
            ))
            if len(relatives) != len(values['relatives']):
                raise CitizenNotFoundError('Relative not found.')
        updated_data = await request.app.storage.update_citizen(import_id, citizen_id, values)
    except CitizenNotFoundError as e:
        raise DataValidationError('You try to set non existent citizens.') from e
    return web.json_response(data={'data': updated_data})


async def get_citizens(request):
    import_id = int(request.match_info['import_id'])
    citizens = list(await(request.app.storage.get_citizens(import_id)))
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
