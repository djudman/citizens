import unittest

from citizens.data import (
    validate_citizen_data, DataValidationError
)


class TestData(unittest.TestCase):
    def test_new_citizen(self):
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
        validate_citizen_data(data)

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
        # with self.assertRaises(DataValidationError) as e:
        #     validate_import_data(import_data)

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
        # with self.assertRaises(DataValidationError) as e:
        #     validate_import_data(import_data)
