from datetime import datetime
from typing import List

__all__ = ['validate_import_data']

class InvalidImportData(Exception):
    pass


class InvalidCitizenData(InvalidImportData):
    pass


class InvalidValue(InvalidCitizenData):
    pass


class Field:
    def __init__(self, *, required=True, value_type=object):
        self.required = required
        self._value_type = value_type

    def validate(self, value):
        self._check_type(value)

    def _check_type(self, value):
        if isinstance(value, self._value_type):
            return
        expected_type_name = self._value_type.__name__
        type_name = type(value).__name__
        raise InvalidValue(f'Invalid type. Expected `{expected_type_name}`, '\
                           f'got `{type_name}`.')


class String(Field):
    def __init__(self, *, min_length=0, values=None, letter_or_digit_required=False):
        super().__init__(value_type=str)
        self._min_length = min_length
        self._letter_or_digit_required = letter_or_digit_required
        self._values = values

    def validate(self, value):
        super().validate(value)
        if len(value) < self._min_length:
            raise InvalidValue('Invalid length')
        if self._letter_or_digit_required and not self._has_letter_or_digit(value):
            raise InvalidValue('At least one digit or letter required.')
        if self._values is not None and value not in self._values:
            raise InvalidValue('Unexpected value.')

    def _has_letter_or_digit(self, value):
        return any(map(lambda s: s.isdigit() or s.isalpha(), value))


class ListOf(Field):
    def __init__(self, inner_type, unique=False):
        super().__init__(value_type=list)
        self._inner_type = inner_type
        self._unique = unique

    def validate(self, value):
        super().validate(value)
        if any(not isinstance(element, self._inner_type) for element in value):
            raise InvalidValue('Invalid element type.')
        if self._unique and len(value) > len(set(value)):
            raise InvalidValue('All elements must be unique.')


def validate_import_data(data):
    non_existent_relatives = set()
    relatives_by_cid = {}

    citizens = (validate_citizen_data(citizen_data) for citizen_data in data)
    for citizen in citizens:
        cid = citizen['citizen_id']
        # Если уже встречали этот id, значит он не уникальный в этой выборке
        if cid in relatives_by_cid:
            raise InvalidImportData(f'Non unique citizen_id `{cid}`')
        relatives_by_cid[cid] = set(citizen['relatives'])
        # Собираем id родственников, которых еще не встречали в выборке.
        # Потенциально их может не оказаться вообще
        non_seen_relatives = filter(lambda rid: rid not in relatives_by_cid,
                                    citizen['relatives'])
        non_existent_relatives.update(non_seen_relatives)
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


def validate_citizen_data(data, all_fields_required=True):
    integer = Field(value_type=int)
    string = String(min_length=1, letter_or_digit_required=True)
    fields = {
        'citizen_id': integer,
        'town': string,
        'street': string,
        'building': string,
        'apartment': integer,
        'name': String(min_length=1),
        'birth_date': String(min_length=10),
        'gender': String(values=('male', 'female')),
        'relatives': ListOf(int, unique=True),
    }
    for name, field in fields.items():
        if all_fields_required and name not in data:
            raise InvalidCitizenData(f'Attribute {name} not found')
        # TODO: А если придет "лишний" атрибут? Считать ошибкой?
        if name in data:
            value = data[name]
            field.validate(value)
    if 'relatives' in data and data['citizen_id'] in data['relatives']:
        raise InvalidCitizenData('Self in relatives')
    if 'birth_date' in data:
        _validate_birth_date(data)
    return data


def _validate_birth_date(citizen_data):
    try:
        datetime.strptime(citizen_data['birth_date'], '%d.%m.%Y')
    except ValueError as e:
        cid = citizen_data.get('citizen_id', '<no value>')
        err = f'Invalid format of `birth_date` for citizen `{cid}`'
        raise InvalidValue(err) from e
