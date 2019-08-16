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
    storage = request.app.storage
    validate_import_data(import_data)
    import_id = await storage.generate_import_id() # TODO: тут всё ещё есть проблема
    await storage.new_import(import_id, import_data)
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
    # TODO: ускорить
    # [{$project: {_id:1, citizen_id: 1, relatives: 1, birth_date: {$dateFromString: {dateString: "$birth_date", format: "%d.%m.%Y"}}, num_relatives: {$size: "$relatives"}}}, {$match: { num_relatives: {$gt: 0}}}]
    import_id = int(request.match_info['import_id'])
    presents_by_month = {month: [] for month in range(1, 13)}
    async for citizen in request.app.storage.get_citizens(import_id):
        num_birthdays_by_month = {month: 0 for month in range(1, 13)}
        for cid in citizen['relatives']:
            relative_data = await request.app.storage.get_one_citizen(
                import_id, cid, return_fields=['birth_date'])
            dt = datetime.strptime(relative_data['birth_date'], '%d.%m.%Y')  # TODO: может регулярками быстрее?
            month = dt.month
            num_birthdays_by_month[month] += 1
        citizen_id = citizen['citizen_id']
        for month, cnt in num_birthdays_by_month.items():
            if cnt == 0:
                continue
            presents_by_month[month].append({
                'citizen_id': citizen_id,
                'presents': cnt,
            })
    return web.json_response(data={'data': presents_by_month})


async def get_age_percentiles(request):
    import_id = int(request.match_info['import_id'])
    ages_by_town = {}
    current_year = datetime.now().year
    async for data in request.app.storage.get_citizens(import_id):
        town = data['town']
        if town not in ages_by_town:
            ages_by_town[town] = []
        birth_dt = datetime.strptime(data['birth_date'], '%d.%m.%Y')
        age = current_year - birth_dt.year
        ages_by_town[town].append(age)

    age_percentiles = []
    percentile = functools.partial(np.percentile, interpolation='linear')
    age_percentiles = [
        {
            'town': town,
            'p50': round(percentile(ages, 50), 2),
            'p75': round(percentile(ages, 75), 2),
            'p99': round(percentile(ages, 99), 2),
        } for town, ages in ages_by_town.items()
    ]
    return web.json_response(data={'data': age_percentiles})
