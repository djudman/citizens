import datetime
import re


class DataValidationError(Exception):
    pass


class SchemaValidationError(DataValidationError):
    pass


class FieldValidationError(SchemaValidationError):
    pass


class Field:
    def validate(self, value):
        pass

    def _check_type(self, value, expected_type):
        if not isinstance(value, expected_type):
            message = 'invalid type (`{expected}` expected, got `{got}`)'.format(
                expected = expected_type.__name__, got = type(value).__name__)
            raise FieldValidationError(message)


class PositiveInteger(Field):
    def validate(self, value):
        self._check_type(value, int)
        if value <= 0:
            raise FieldValidationError('value must be > 0')


class String(Field):
    def __init__(self, min_length=0, max_length=None, letter_or_digit_required=False, values=None):
        self._min_length = min_length
        self._max_length = max_length
        self._letter_or_digit_required = letter_or_digit_required
        self._values = values

    def validate(self, value):
        self._check_type(value, str)
        min_length = self._min_length
        max_length = self._max_length
        if min_length > 0 and len(value) < min_length:
            message = f'too short value. Minimum {min_length} symbols expected'
            raise FieldValidationError(message)
        if max_length is not None and len(value) > max_length:
            message = f'too long value. Maximum {max_length} symbols expected'
            raise FieldValidationError(message)
        letters_digits = filter(lambda s: s.isalpha() or s.isdigit(), value)
        if self._letter_or_digit_required and not any(letters_digits):
            raise FieldValidationError('at least one digit or letter required')
        if self._values and value not in self._values:
            possible_values = ', '.join(self._values)
            message = f'unexpected value `{value}`. Expected values: {possible_values}'
            raise FieldValidationError(message)


class BirthDate(String):
    def validate(self, value):
        super().validate(value)
        regex = re.compile(r'^(?P<day>\d\d?)\.(?P<month>\d\d?)\.(?P<year>\d{4})$')
        matched = regex.match(value)
        if not matched:
            raise FieldValidationError('invalid format. `dd.mm.yyyy` expected')
        try:
            match = lambda name: int(matched.group(name))
            day, month, year = match('day'), match('month'), match('year')
            date = datetime.date(year, month, day)
        except Exception as e:
            raise FieldValidationError(str(e))
        today = datetime.datetime.utcnow().date()
        if date >= today:
            raise FieldValidationError('value must be earlier than today')


class List(Field):
    def __init__(self, element_type, unique=False):
        self._element_type = element_type
        self._unique = unique

    def validate(self, values):
        self._check_type(values, list)
        if isinstance(self._element_type, Field):
            list(map(lambda v: self._element_type.validate(v), values))
        elif any(filter(lambda v: not isinstance(v, self._element_type), values)):
            raise FieldValidationError('invalid element type')
        if self._unique and len(values) != len(set(values)):
            raise FieldValidationError('elements must be unique')


class CitizenSchema:
    citizen_id = PositiveInteger()
    town = String(letter_or_digit_required=True, max_length=256)
    street = String(letter_or_digit_required=True, max_length=256)
    building = String(letter_or_digit_required=True, max_length=256)
    apartment = PositiveInteger()
    name = String(min_length=1, max_length=256)
    birth_date = BirthDate()
    gender = String(values=('male', 'female'))
    relatives = List(element_type=PositiveInteger(), unique=True)

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        fields = {k: v for k, v in cls.__dict__.items() if isinstance(v, Field)}
        obj.fields = fields
        obj.fields_cnt = len(fields)
        return obj

    def validate(self, data: dict, partial=False):
        try:
            fields = self.fields
            for name, value in data.items():
                if name not in fields:
                    raise SchemaValidationError(f'unknown field')
                fields[name].validate(value)
            if not partial and self.fields_cnt != len(data):
                raise SchemaValidationError('all fields required')
        except FieldValidationError as e:
            err = str(e)
            raise SchemaValidationError(f'Field `{name}` is invalid: {err}')


def validate_citizens(citizens: list):
    relatives_by_cid = {}
    non_existent_relatives = set()
    schema = CitizenSchema()
    for citizen in citizens:
        schema.validate(citizen)
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
