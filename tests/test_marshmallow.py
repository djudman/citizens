import time
import unittest

from citizens.data import CitizenValidator

marshmallow_is_not_installed = False
try:
    from marshmallow import Schema, fields, validate, validates, ValidationError


    def letter_or_digit_required(value):
        valid = any(filter(lambda s: s.isalpha() or s.isdigit(), value))
        if not valid:
            raise ValidationError('At least one letter or digit required')


    def validate_int(value):
        if value <= 0:
            raise ValidationError('Value must be positive')


    class CitizenSchema(Schema):
        citizen_id = fields.Int(strict=True, validate=validate_int)
        town = fields.Str(validate=letter_or_digit_required)
        street = fields.Str(validate=letter_or_digit_required)
        building = fields.Str(validate=letter_or_digit_required)
        apartment = fields.Int(strict=True, validate=validate_int)
        name = fields.Str(validate=validate.Length(min=1))
        birth_date = fields.Date('%d.%m.%Y')
        gender = fields.Str(validate=validate.OneOf(('male', 'female')))
        relatives = fields.List(fields.Int(strict=True, validate=validate_int))

        @validates('relatives')
        def validate_relatives(self, value):
            return len(value) == len(set(value))

except ImportError:
    marshmallow_is_not_installed = True


@unittest.skipIf(marshmallow_is_not_installed, 'Marshmallow is not installed.')
class TestMarshmallow(unittest.TestCase):
    def setUp(self):
        self.citizens = [self._make_citizen_data(i + 1) for i in range(10000)]
        invalid_data = self._make_citizen_data(-1)
        self.citizens.append(invalid_data)

    def _make_citizen_data(self, citizen_id):
        return {
            "citizen_id": citizen_id,
            "town": "Амстердам",
            "street": "Ленина",
            "building": "16к7стр5",
            "apartment": 365,
            "name": "Иванов Сергей Иванович",
            "birth_date": "01.02.1997",
            "gender": "male",
            "relatives": [1, 2, 3]
        }

    def test_speed(self):
        for _ in range(1):
            t1 = time.time()
            schema = CitizenSchema()
            for data in self.citizens:
                errors = schema.validate(data)
                if errors:
                    break
            marshmallow = time.time() - t1
            validator = CitizenValidator()
            t1 = time.time()
            try:
                for data in self.citizens:
                    validator.validate(data)
            except Exception:
                pass
            my_one = time.time() - t1
            print('Marshmallow: {0} sec\nCustom: {1} sec\nRatio: x{2}'.format(
                round(marshmallow, 3),
                round(my_one, 3),
                round(marshmallow / my_one, 1)
            ))
