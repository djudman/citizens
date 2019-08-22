import functools
import numpy as np

from aiohttp import web
from aiojobs.aiohttp import atomic

from citizens.schema import (
    validate_citizens, CitizenSchema, DataValidationError
)
from citizens.storage import CitizenNotFound


class CitizensBadRequest(Exception):
    pass


@atomic
async def new_import(request):
    import_data = await request.json()
    if 'citizens' not in import_data:
        raise CitizensBadRequest('Key `citizens` not found.')
    citizens = import_data['citizens']
    try:
        validate_citizens(citizens)
    except DataValidationError as e:
        raise CitizensBadRequest('Invalid citizens data') from e
    import_id = await request.app.storage.import_citizens(citizens)
    out = {'data': {'import_id': import_id}}
    return web.json_response(data=out, status=201)


@atomic
async def update_citizen(request):
    import_id = int(request.match_info['import_id'])
    citizen_id = int(request.match_info['citizen_id'])
    values = await request.json()
    if not values:
        raise CitizensBadRequest('No values.')
    if 'citizen_id' in values:
        raise CitizensBadRequest('Forbidden to update field `citizen_id`.')
    try:
        CitizenSchema().validate(values, partial=True)
    except DataValidationError as e:
        raise CitizensBadRequest('Invalid values') from e
    storage = request.app.storage
    if 'relatives' in values:
        new_relatives = values['relatives']
        relatives = list(await storage.get_citizens(
            import_id,
            filter={'citizen_id': new_relatives},  # NOTE: citizen_id in new_relatives
            return_fields=['citizen_id']
        ))
        if len(relatives) != len(new_relatives):
            raise CitizensBadRequest('Invalid value for `relatives`.')
    try:
        updated_data = await storage.update_citizen(import_id, citizen_id, values)
    except CitizenNotFound as e:
        raise CitizensBadRequest() from e
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
