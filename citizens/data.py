from datetime import datetime
from typing import List


class DataValidationError(Exception):
    pass


class CitizenValidationError(DataValidationError):
    pass


class FieldValidationError(CitizenValidationError):
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
        raise FieldValidationError('Invalid value type. '\
            f'Expected `{expected_type_name}`, got `{type_name}`.')


class String(Field):
    def __init__(self, *, min_length=0, values=None, letter_or_digit_required=False):
        super().__init__(value_type=str)
        self._min_length = min_length
        self._letter_or_digit_required = letter_or_digit_required
        self._values = values

    def validate(self, value):
        super().validate(value)
        if self._min_length is not None and len(value) < self._min_length:
            raise FieldValidationError('Too short value. '
                'Minimum {0} symbols expected.'.format(self._min_length))
        if self._letter_or_digit_required and not self.has_letter_or_digit(value):
            raise FieldValidationError(f'At least one digit or letter required. Got: `{value}`')
        if self._values is not None and value not in self._values:
            possible_values = ', '.join(self._values)
            raise FieldValidationError(f'Unexpected value `{value}`. '\
                f'Possible values: {possible_values}')

    def has_letter_or_digit(self, value):
        return any(map(lambda s: s.isdigit() or s.isalpha(), value))


class ListOf(Field):
    def __init__(self, element_type, unique=False):
        super().__init__(value_type=list)
        self._element_type = element_type
        self._unique = unique

    def validate(self, value):
        super().validate(value)
        if any(not isinstance(element, self._element_type) for element in value):
            raise FieldValidationError('Invalid element type.')
        if self._unique and len(value) != len(set(value)):
            raise FieldValidationError('All elements must be unique.')


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
    # TODO: как-то не очень, придумать получше
    if all_fields_required and len(fields) != len(data):
        raise CitizenValidationError('Invalid fields set.')
    for name, value in data.items():
        if value is None:
            raise CitizenValidationError('Value cannot be null.')
        if name not in fields:
            # NOTE: считаем лишний атрибут ошибкой
            raise CitizenValidationError(f'Unknown field `{name}`.')
        try:
            fields[name].validate(value)
        except FieldValidationError as e:
            raise CitizenValidationError(f'Invalid value for `{name}`.') from e
    if 'birth_date' in data:
        _validate_birth_date(data)
    return data


def _validate_birth_date(citizen_data):
    try:
        datetime.strptime(citizen_data['birth_date'], '%d.%m.%Y')
    except ValueError as e:
        cid = citizen_data.get('citizen_id', '<no value>')
        err = f'Invalid format of `birth_date` for citizen `{cid}`'
        raise FieldValidationError(err) from e
