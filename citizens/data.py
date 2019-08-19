import datetime
import re
from typing import List


class DataValidationError(Exception):
    pass


class CitizenValidationError(DataValidationError):
    pass


class FieldValidationError(CitizenValidationError):
    pass


class Field:
    def __init__(self, *, required=True, value_type=object, validator=None):
        self.required = required
        self._value_type = value_type
        self._validator = validator

    def validate(self, value):
        if value is None:
            raise FieldValidationError('Value is None')
        if not isinstance(value, self._value_type):
            type_name = type(value).__name__
            expected = self._value_type.__name__
            message = f'Invalid value type. Expected `{expected}`, got `{type_name}`.'
            raise FieldValidationError(message)
        if self._validator is not None and not self._validator(value):
            raise FieldValidationError(f'Invalid value `{value}`')


class String(Field):
    def __init__(self, *, min_length=0, values=None, letter_or_digit_required=False):
        super().__init__(value_type=str)
        self._min_length = min_length
        self._letter_or_digit_required = letter_or_digit_required
        self._values = values

    def validate(self, value):
        super().validate(value)
        min_length = self._min_length
        if min_length > 0 and len(value) < min_length:
            message = f'Too short value. Minimum {min_length} symbols expected.'
            raise FieldValidationError(message)
        letters_digits = filter(lambda s: s.isalpha() or s.isdigit(), value)
        if self._letter_or_digit_required and not any(letters_digits):
            raise FieldValidationError(f'At least one digit or letter required. Got: `{value}`')
        if self._values and value not in self._values:
            possible_values = ', '.join(self._values)
            message = f'Unexpected value `{value}`. Possible values: {possible_values}'
            raise FieldValidationError(message)


class BirthDate(Field):
    def __init__(self):
        super().__init__(value_type=str)

    def validate(self, value):
        super().validate(value)
        try:
            regex = re.compile(r'^(?P<day>\d\d?)\.(?P<month>\d\d?)\.(?P<year>\d{4})$')
            matched = regex.match(value)
            if not matched:
                raise FieldValidationError('Invalid date format.')
            day, month, year = int(matched.group('day')), int(matched.group('month')), int(matched.group('year'))
            date = datetime.date(year=year, month=month, day=day)
        except Exception as e:
            raise FieldValidationError(str(e))
        today = datetime.datetime.utcnow().date()
        if date >= today:
            raise FieldValidationError('Birth date must be earlier than today.')


class ListOf(Field):
    def __init__(self, element_type, unique=False):
        super().__init__(value_type=list)
        self._element_type = element_type
        self._unique = unique

    def validate(self, value):
        super().validate(value)
        if any(filter(lambda v: not isinstance(v, self._element_type), value)):
            raise FieldValidationError('Invalid element type.')
        if any(filter(lambda v: v <= 0, value)):
            raise FieldValidationError('All elements must be positive.')
        if self._unique and len(value) != len(set(value)):
            raise FieldValidationError('All elements must be unique.')


class CitizenValidator:
    def __init__(self):
        integer = Field(value_type=int, validator=lambda v: v > 0)
        string = String(letter_or_digit_required=True)
        self._fields = {
            'citizen_id': integer,
            'town': string,
            'street': string,
            'building': string,
            'apartment': integer,
            'name': String(min_length=1),
            'birth_date': BirthDate(),
            'gender': String(values=set({'male', 'female'})),
            'relatives': ListOf(int, unique=True),
        }

    def validate(self, data, all_fields_required=True):
        fields = self._fields
        if all_fields_required and len(fields) != len(data):
            raise CitizenValidationError('Invalid fields set.')
        name = None
        try:
            for name, value in data.items():
                fields = self._fields
                if name not in fields:
                    # считаем лишний атрибут ошибкой
                    raise FieldValidationError(f'Unknown field `{name}`.')
                fields[name].validate(value)
        except FieldValidationError as e:
            raise CitizenValidationError(f'Field `{name}` is invalid.') from e
        return data


def validate_import_data(import_data: list):
    relatives_by_cid = {}
    non_existent_relatives = set()
    citizen_validator = CitizenValidator()
    for citizen in import_data:
        citizen_validator.validate(citizen)
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
