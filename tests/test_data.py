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
        import_data = [
            {
                "citizen_id": 1,
                "town": "Амстердам",
                "street": "Ленина",
                "building": "16к7стр5",
                "apartment": 365,
                "name": "Иванов Сергей Иванович",
                "birth_date": "31.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `birth_date` is invalid.')

    def test_birth_date_invalid_format(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Амстердам",
                "street": "Ленина",
                "building": "16к7стр5",
                "apartment": 365,
                "name": "Иванов Сергей Иванович",
                "birth_date": "11/02/1997",
                "gender": "male",
                "relatives": []
            },
        ]
        with self.assertRaises(DataValidationError) as e:
            validate_import_data(import_data)
        self.assertEqual(str(e.exception), 'Field `birth_date` is invalid.')
