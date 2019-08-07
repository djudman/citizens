import unittest

from citizens.data import Citizen


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
        citizen = Citizen(**data)
