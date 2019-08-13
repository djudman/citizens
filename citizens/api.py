import asyncio
import math
import numpy as np
from datetime import datetime
from itertools import groupby

from aiohttp import web

from citizens.data import validate_citizen_data, DataValidationError
from citizens.storage import CitizenNotFoundError


class CitizensApiError(Exception):
    pass


async def new_import(request):
    import_data = await asyncio.shield(request.json())

    storage = request.app.storage
    import_id = await storage.generate_import_id()
    citizens = (validate_citizen_data(citizen_data) for citizen_data in import_data)

    non_existent_relatives = set()
    relatives_by_cid = {}
    for citizen in citizens:
        cid = citizen['citizen_id']
        # Если уже встречали этот id, значит он не уникальный в этой выборке
        if cid in relatives_by_cid:
            raise DataValidationError(f'Non unique citizen_id `{cid}`')
        relatives_by_cid[cid] = set(citizen['relatives'])
        # Собираем id родственников, которых еще не встречали в выборке.
        # Потенциально их может не оказаться вообще
        non_seen_relatives = filter(lambda rid: rid not in relatives_by_cid,
                                    citizen['relatives'])
        non_existent_relatives.update(non_seen_relatives)
        # Удаляем текущий cid из множества несуществующих родственников (если есть)
        if cid in non_existent_relatives:
            non_existent_relatives.remove(cid)
        await storage.insert_citizen(import_id, citizen)

    # TODO: может какой-то класс-валидатор придумать?
    # Если после перебора всех жителей у нас остались не найденные родственники, ошибка
    if non_existent_relatives:
        cnt = len(non_existent_relatives)
        raise DataValidationError(f'There are {cnt} non existent relatives')
    # Проверяем родственные связи. Второй раз проходим по всем. TODO: подумать
    # может всё-таки как-то можно ужать в один проход?
    for cid, relatives in relatives_by_cid.items():
        for relative_cid in relatives:
            if cid not in relatives_by_cid[relative_cid]:
                raise DataValidationError(f'Invalid relatives for `{cid}`')

    # TODO: удалить данные, если была ошибка валидации

    out = {'data': {'import_id': import_id}}
    return web.json_response(data=out, status=201)


async def update_citizen(request):
    import_id = int(request.match_info['import_id'])
    citizen_id = int(request.match_info['citizen_id'])
    citizen_data = await asyncio.shield(request.json())
    if 'citizen_id' in citizen_data:
        raise DataValidationError('Forbidden to update field `citizen_id`.')
    validate_citizen_data(citizen_data, all_fields_required=False)
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
        for month, dates in groupby(relatives_birthdays, key=lambda date: date.month):
            presents_by_month[month].append({
                'citizen_id': citizen['citizen_id'],
                'presents': len(list(dates)),
            })
    return web.json_response(data={'data': presents_by_month})


async def get_age_percentiles(request):
    import_id = int(request.match_info['import_id'])
    citizens = [data async for data in request.app.storage.get_citizens(import_id)]
    age_percentiles = []
    for town, citizens_in_town in groupby(citizens, key=lambda data: data['town']):
        ages = []
        for citizen in citizens_in_town:
            # TODO: вычислить возраст просто как разницу между текущим годом и годом рождения
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
