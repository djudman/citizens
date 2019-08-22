import unittest

from citizens.schema import (
    CitizenSchema, DataValidationError, validate_citizens
)


class TestData(unittest.TestCase):
    def setUp(self):
        self.schema = CitizenSchema()

    def get_fields(self):
        return self.schema.fields.keys()

    def get_default_citizen_data(self, values=None):
        data = {
            "citizen_id": 1,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Сергей Иванович",
            "birth_date": "17.04.1999",
            "gender": "male",
            "relatives": []
        }
        if values:
            data.update(values)
        return data

    # Этот тест не проверяет родственные связи (и не должен)
    def test_valid_citizen_data(self):
        data = {
            "citizen_id": 1,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Сергей Иванович",
            "birth_date": "17.04.1999",
            "gender": "male",
            "relatives": [2]
        }
        self.schema.validate(data)

    def test_invalid_citizen_id(self):
        invalid_values = [
            (0, 'Field `citizen_id` is invalid: value must be > 0'),
            (-1, 'Field `citizen_id` is invalid: value must be > 0'),
            (1.0, 'Field `citizen_id` is invalid: invalid type (`int` expected, got `float`)'),
            ('', 'Field `citizen_id` is invalid: invalid type (`int` expected, got `str`)'),
            ('1', 'Field `citizen_id` is invalid: invalid type (`int` expected, got `str`)'),
            ('[]', 'Field `citizen_id` is invalid: invalid type (`int` expected, got `str`)'),
            ('a', 'Field `citizen_id` is invalid: invalid type (`int` expected, got `str`)'),
            (b'1', 'Field `citizen_id` is invalid: invalid type (`int` expected, got `bytes`)'),
            (None, 'Field `citizen_id` is invalid: invalid type (`int` expected, got `NoneType`)'),
        ]
        for value, err in invalid_values:
            citizen_data = self.get_default_citizen_data({ 'citizen_id': value })
            with self.assertRaises(DataValidationError) as ctx:
                validate_citizens([citizen_data])
            self.assertEqual(str(ctx.exception), err)

    def test_invalid_town(self):
        invalid_values = [
            ('', 'Field `town` is invalid: at least one digit or letter required'),
            (None, 'Field `town` is invalid: invalid type (`str` expected, got `NoneType`)'),
            (' ', 'Field `town` is invalid: at least one digit or letter required'),
            ('-', 'Field `town` is invalid: at least one digit or letter required'),
            ('_', 'Field `town` is invalid: at least one digit or letter required'),
            ('a' * 257, 'Field `town` is invalid: too long value. Maximum 256 symbols expected'),
            (b'1', 'Field `town` is invalid: invalid type (`str` expected, got `bytes`)'),
            ('_ - _=+*.', 'Field `town` is invalid: at least one digit or letter required'),
        ]
        for value, err in invalid_values:
            citizen_data = self.get_default_citizen_data({ 'town': value })
            with self.assertRaises(DataValidationError) as ctx:
                validate_citizens([citizen_data])
            self.assertEqual(str(ctx.exception), err)

    def test_invalid_street(self):
        invalid_values = [
            ('', 'Field `street` is invalid: at least one digit or letter required'),
            (None, 'Field `street` is invalid: invalid type (`str` expected, got `NoneType`)'),
            (' ', 'Field `street` is invalid: at least one digit or letter required'),
            ('-', 'Field `street` is invalid: at least one digit or letter required'),
            ('_', 'Field `street` is invalid: at least one digit or letter required'),
            ('a' * 257, 'Field `street` is invalid: too long value. Maximum 256 symbols expected'),
            (b'1', 'Field `street` is invalid: invalid type (`str` expected, got `bytes`)'),
            ('_ - _=+*.', 'Field `street` is invalid: at least one digit or letter required'),
        ]
        for value, err in invalid_values:
            citizen_data = self.get_default_citizen_data({ 'street': value })
            with self.assertRaises(DataValidationError) as ctx:
                validate_citizens([citizen_data])
            self.assertEqual(str(ctx.exception), err)

    def test_invalid_building(self):
        invalid_values = [
            ('', 'Field `building` is invalid: at least one digit or letter required'),
            (None, 'Field `building` is invalid: invalid type (`str` expected, got `NoneType`)'),
            (' ', 'Field `building` is invalid: at least one digit or letter required'),
            ('-', 'Field `building` is invalid: at least one digit or letter required'),
            ('_', 'Field `building` is invalid: at least one digit or letter required'),
            ('a' * 257, 'Field `building` is invalid: too long value. Maximum 256 symbols expected'),
            (b'1', 'Field `building` is invalid: invalid type (`str` expected, got `bytes`)'),
            ('_ - _=+*.', 'Field `building` is invalid: at least one digit or letter required'),
        ]
        for value, err in invalid_values:
            citizen_data = self.get_default_citizen_data({ 'building': value })
            with self.assertRaises(DataValidationError) as ctx:
                validate_citizens([citizen_data])
            self.assertEqual(str(ctx.exception), err)

    def test_invalid_apartment(self):
        invalid_values = [
            ('', 'Field `apartment` is invalid: invalid type (`int` expected, got `str`)'),
            (None, 'Field `apartment` is invalid: invalid type (`int` expected, got `NoneType`)'),
            ('1', 'Field `apartment` is invalid: invalid type (`int` expected, got `str`)'),
            (0, 'Field `apartment` is invalid: value must be > 0'),
            (-2, 'Field `apartment` is invalid: value must be > 0'),
            (b'1', 'Field `apartment` is invalid: invalid type (`int` expected, got `bytes`)'),
            (5.0, 'Field `apartment` is invalid: invalid type (`int` expected, got `float`)'),
        ]
        for value, err in invalid_values:
            citizen_data = self.get_default_citizen_data({ 'apartment': value })
            with self.assertRaises(DataValidationError) as ctx:
                validate_citizens([citizen_data])
            self.assertEqual(str(ctx.exception), err)

    def test_invalid_name(self):
        invalid_values = [
            ('', 'Field `name` is invalid: too short value. Minimum 1 symbols expected'),
            (None, 'Field `name` is invalid: invalid type (`str` expected, got `NoneType`)'),
            (0, 'Field `name` is invalid: invalid type (`str` expected, got `int`)'),
            (-2, 'Field `name` is invalid: invalid type (`str` expected, got `int`)'),
            (b'1', 'Field `name` is invalid: invalid type (`str` expected, got `bytes`)'),
            (5.0, 'Field `name` is invalid: invalid type (`str` expected, got `float`)'),
            ('a' * 257, 'Field `name` is invalid: too long value. Maximum 256 symbols expected'),
        ]
        for value, err in invalid_values:
            citizen_data = self.get_default_citizen_data({ 'name': value })
            with self.assertRaises(DataValidationError) as ctx:
                validate_citizens([citizen_data])
            self.assertEqual(str(ctx.exception), err)

    def test_non_existent_relatives(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": [2]
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_citizens(citizens)
        self.assertEqual(str(e.exception), 'There are 1 non existent relatives')

    def test_non_mutual_relatives(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": [2]
            },
            {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            }
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_citizens(citizens)
        self.assertEqual(str(e.exception), 'Invalid relatives for `1`')

    def test_null_values(self):
        for name in self.get_fields():
            citizen_data = self.get_default_citizen_data({name: None})
            with self.assertRaises(DataValidationError) as e:
                validate_citizens([citizen_data])
            self.assertTrue(str(e.exception).startswith(f'Field `{name}` is invalid: invalid type'))

    def test_non_existent_field(self):
        for name in self.get_fields():
            citizen_data = self.get_default_citizen_data()
            del citizen_data[name]
            with self.assertRaises(DataValidationError) as e:
                validate_citizens([citizen_data])
            self.assertEqual(str(e.exception), f'all fields required')

    def test_gender_invalid_value(self):
        invalid_values = [
            ('mal', 'Field `gender` is invalid: unexpected value `mal`. Expected values: male, female'),
            ('males', 'Field `gender` is invalid: unexpected value `males`. Expected values: male, female'),
            ('emale', 'Field `gender` is invalid: unexpected value `emale`. Expected values: male, female'),
            ('femаle', 'Field `gender` is invalid: unexpected value `femаle`. Expected values: male, female'),  # русская буква `а`
            ('', 'Field `gender` is invalid: unexpected value ``. Expected values: male, female'),
            (None, 'Field `gender` is invalid: invalid type (`str` expected, got `NoneType`)'),
            (0, 'Field `gender` is invalid: invalid type (`str` expected, got `int`)'),
        ]
        for value, err in invalid_values:
            citizen_data = self.get_default_citizen_data({'gender': value})
            with self.assertRaises(DataValidationError) as ctx:
                validate_citizens([citizen_data])
            self.assertEqual(str(ctx.exception), err)

    def test_relatives_invalid_value(self):
        invalid_values = [
            (['2'], 'Field `relatives` is invalid: invalid type (`int` expected, got `str`)'),
            ([0], 'Field `relatives` is invalid: value must be > 0'),
            ([-1], 'Field `relatives` is invalid: value must be > 0'),
            (['a'], 'Field `relatives` is invalid: invalid type (`int` expected, got `str`)'),
            ([1, 1], 'Field `relatives` is invalid: elements must be unique'),
            ([2, 2], 'Field `relatives` is invalid: elements must be unique'),
            ([1, 1, 2], 'Field `relatives` is invalid: elements must be unique')
        ]
        for value, err in invalid_values:
            citizen_data = self.get_default_citizen_data({'relatives': value})
            with self.assertRaises(DataValidationError) as e:
                validate_citizens([citizen_data])
            self.assertEqual(str(e.exception), err)

    def test_birth_date_invalid_value(self):
        citizen_data = {
            "citizen_id": 1,
            "town": "Амстердам",
            "street": "Ленина",
            "building": "16к7стр5",
            "apartment": 365,
            "name": "Иванов Сергей Иванович",
            "birth_date": "31.02.1997",
            "gender": "male",
            "relatives": []
        }
        date_invalid_values = [
            '31.02.1997', '29.02.2019', '00.00.0000',
            '001.02.1997', '01.002.1997', '01.02.01997',
            '11/02/1997', '11-02-1997',
            '-1.1.1900', '1.-1.1900', '1.1.-190',
            '01.01.5020',
            r'1\.1\.1111',
            '21.02.20191', '21.02.2019a',
            ' 21.02.2019', '21.02.2019 ',
            '21.02. 2019', ' 1.2.2001', '1. 2.2001', '1.2.20 1',
            '.04.2019', '24..2019', '26.01.', '..',
        ]
        for value in date_invalid_values:
            citizen_data['birth_date'] = value
            with self.assertRaises(DataValidationError) as ctx:
                validate_citizens([citizen_data])
            self.assertTrue(str(ctx.exception).startswith('Field `birth_date` is invalid: '))

    def test_birth_date_valid_value(self):
        citizen_data = {
            "citizen_id": 1,
            "town": "Амстердам",
            "street": "Ленина",
            "building": "16к7стр5",
            "apartment": 365,
            "name": "Иванов Сергей Иванович",
            "birth_date": '1.1.1900',
            "gender": "male",
            "relatives": []
        }
        date_valid_values = [
            '1.02.1997',
            '1.2.2001',
            '1.1.0001',
            '29.02.2016',
        ]
        for value in date_valid_values:
            citizen_data['birth_date'] = value
            validate_citizens([citizen_data])
