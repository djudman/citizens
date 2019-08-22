import unittest

from citizens.data import (
    CitizenValidator, DataValidationError, validate_import_data
)


class TestData(unittest.TestCase):
    def setUp(self):
        self.validator = CitizenValidator()

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
        self.validator.validate(data)

    def test_non_existent_relatives(self):
        import_data = [
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
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'There are 1 non existent relatives')


    def test_null_values(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": None,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `apartment` is invalid.')

    def test_town_is_empty(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 3,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `town` is invalid.')

    def test_street_is_empty(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Амстердам",
                "street": "",
                "building": "16к7стр5",
                "apartment": 3,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `street` is invalid.')

    def test_building_is_empty(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Амстердам",
                "street": "Ленина",
                "building": "",
                "apartment": 3,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `building` is invalid.')

    def test_apartment_is_not_number(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Амстердам",
                "street": "Ленина",
                "building": "16к7стр5",
                "apartment": '365',
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `apartment` is invalid.')

    def test_name_is_empty(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Амстердам",
                "street": "Ленина",
                "building": "16к7стр5",
                "apartment": 365,
                "name": "",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `name` is invalid.')

    def test_gender_invalid_value(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Амстердам",
                "street": "Ленина",
                "building": "16к7стр5",
                "apartment": 365,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "males",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `gender` is invalid.')

    def test_citizen_id_invalid_value(self):
        import_data = [
            {
                "citizen_id": -1,
                "town": "Амстердам",
                "street": "Ленина",
                "building": "16к7стр5",
                "apartment": 365,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `citizen_id` is invalid.')

    def test_relative_id_invalid_value(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Амстердам",
                "street": "Ленина",
                "building": "16к7стр5",
                "apartment": 365,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": ['2']
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `relatives` is invalid.')

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
                validate_import_data([citizen_data])
            self.assertEqual(str(ctx.exception), 'Field `birth_date` is invalid.')

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
            validate_import_data([citizen_data])
