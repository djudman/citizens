import datetime
import json
import random
import string


class ImportDataGenerator:
    def __init__(self):
        self._next_citizen_id = 1
        self._relatives = {}

    def _generate_string(self, min_length=1, max_length=50):
        return ''.join(
            [random.choice(string.ascii_letters)
             for _ in range(random.randint(min_length, max_length))]
        )

    def _generate_date(self):
        year = random.randint(1900, datetime.datetime.utcnow().date().year - 1)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return datetime.datetime(year=year, month=month, day=day).strftime('%d.%m.%Y')

    def _generate_relatives(self, citizen_id, max_relative_id):
        num_relatives = random.randint(1, 4)
        relative_id = None
        if citizen_id not in self._relatives:
            self._relatives[citizen_id] = set()
        for _ in range(num_relatives):
            while not relative_id or (relative_id in self._relatives[citizen_id]):
                relative_id = random.randint(1, max_relative_id)
            self._relatives[citizen_id].add(relative_id)
            if relative_id not in self._relatives:
                self._relatives[relative_id] = set()
            self._relatives[relative_id].add(citizen_id)

    def generate_citizen_data(self, max_citizen_id):
        citizen_id = self._next_citizen_id
        self._next_citizen_id += 1
        if citizen_id not in self._relatives and random.randint(1, 100) < 30:
            self._generate_relatives(citizen_id, max_citizen_id)
        return {
            'citizen_id': citizen_id,
            'town': random.choice(string.ascii_uppercase),
            'street': self._generate_string(10, 20),
            'building': self._generate_string(2, 6),
            'apartment': random.randint(1, 300),
            'name': self._generate_string(4, 10),
            'birth_date': self._generate_date(),
            'gender': random.choice(['male', 'female']),
            'relatives': [],
        }

    def generate_import_data(self, num_citizens=100):
        self._next_citizen_id = 1
        self._relatives = {}
        citizens_data = [self.generate_citizen_data(num_citizens) for _ in range(num_citizens)]
        out = []
        for citizen_data in citizens_data:
            citizen_id = citizen_data['citizen_id']
            if citizen_id in self._relatives:
                citizen_data['relatives'] = list(self._relatives[citizen_id])
            out.append(citizen_data)
        return {'citizens': out}
