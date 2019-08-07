from dataclasses import dataclass
from datetime import datetime
from typing import List


class InvalidImportData(Exception):
    pass


class InvalidCitizenData(InvalidImportData):
    pass


# class Field:
#     def __init__(self, required=True, checker=None):
#         pass

#     def __get__(self):
#         pass

#     def __set__(self):
#         pass

#     def _validate(self, value):
#         pass


# class Integer(Field):
#     def _validate(self, value):
#         if not isinstance(value, int):
#             raise InvalidCitizenData('')

# class String(Field):
#     def _validate(self, value):
#         if not isinstance(value, int):
#             raise InvalidCitizenData('')


class Citizen:
    citizen_id: int
    town: str
    street: str
    building: str
    apartment: int
    name: str
    birth_date: str
    gender: str
    relatives: List[int]

    def __post_init__(self):
        # check types
        pass


def validate_citizen_data(data):
    return Citizen(**data)


def _validate_birth_date(citizen_data):
    try:
        datetime.strptime(citizen_data['birth_date'], '%d.%m.%Y')
    except ValueError as e:
        cid = citizen_data.get('citizen_id', '<no value>')
        err = f'Invalid format of `birth_date` for citizen `{cid}`'
        raise InvalidImportData(err) from e


def validate_import_data(data):
    non_existent_relatives = set()
    relatives_by_cid = {}

    citizens = (validate_citizen_data(citizen_data) for citizen_data in data)
    for citizen in citizens:
        cid = citizen.citizen_id
        # Если уже встречали этот id, значит он не уникальный в этой выборке
        if cid in relatives_by_cid:
            raise InvalidImportData(f'Non unique citizen_id `{cid}`')
        relatives_by_cid[cid] = set(citizen.relatives)
        # Собираем id родственников, которых еще не встречали в выборке.
        # Потенциально их может не оказаться вообще
        non_seen_relatives = filter(lambda rid: rid not in relatives_by_cid,
                                    citizen.relatives)
        map(non_existent_relatives.add, non_seen_relatives)
        # Удаляем текущий cid из множества несуществующих родственников (если есть)
        if cid in non_existent_relatives:
            non_existent_relatives.remove(cid)

    # Если после перебора всех жителей у нас остались не найденные родственники, ошибка
    if non_existent_relatives:
        cnt = len(non_existent_relatives)
        raise InvalidImportData(f'There are {cnt} non existent relatives')
    # Проверяем родственные связи. Второй раз проходим по всем. TODO: подумать
    # может всё-таки как-то можно ужать в один проход?
    for cid, relatives in relatives_by_cid.items():
        for relative_cid in relatives:
            if cid not in relatives_by_cid[relative_cid]:
                raise InvalidImportData(f'Invalid relatives for `{cid}`')
