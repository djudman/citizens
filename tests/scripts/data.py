import datetime
import json
import random
import string
from os.path import join, realpath, dirname


class ImportDataGenerator:
    def __init__(self):
        self._counter = 1

    def _generate_string(self, min_length=1, max_length=50):
        return ''.join(
            [random.choice(string.ascii_letters)
             for _ in range(random.randint(min_length, max_length))]
        )

    def _generate_date(self):
        year = random.randint(1900, datetime.datetime.now().year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return datetime.datetime(year=year, month=month, day=day).strftime('%d.%m.%Y')

    def _generate_relatives(self, is_orphan=False):
        if is_orphan:
            return []
        return []

    def generate_citizen_data(self):
        self._counter += 1
        return {
            'citizen_id': self._counter,
            'town': self._generate_string(5, 15),
            'street': self._generate_string(10, 20),
            'building': self._generate_string(2, 6),
            'apartment': random.randint(1, 300),
            'name': self._generate_string(4, 10),
            'birth_date': self._generate_date(),
            'gender': random.choice(['male', 'female']),
            'relatives': self._generate_relatives(random.randint(1, 100) > 50),
        }

    def generate_import_data(self, num_citizens=100):
        return (self.generate_citizen_data() for _ in range(num_citizens))

    def generate_tank_ammo(self, filename='ammo.txt', host='84.201.138.48',
                           num_imports=3, num_citizens_in_import=3):
        requests = []
        imports = (self.generate_import_data(num_citizens_in_import) for _ in range(num_imports))
        for import_data in imports:
            str_import_data = json.dumps(list(import_data))
            content_length = len(str_import_data)
            headers = '\r\n'.join([
                'POST /imports HTTP/1.1',
                'Content-Length: {0}'.format(content_length),
                'Host: {0}'.format(host),
                'User-Agent: yandex-tank'
            ])
            request = '{request_headers}\r\n\r\n{body}'.format(
                request_headers=headers,
                body=str_import_data
            )
            requests.append(
                '{request_size} {tag}\n{request}'.format(
                    request_size=len(request),
                    tag='import',
                    request=request
                )
            )
        with open(filename, 'w') as f:
            f.write('\n'.join(requests))


if __name__ == '__main__':
    ImportDataGenerator().generate_tank_ammo(
        filename=join(realpath(dirname(__file__)), 'yandex-tank/ammo.txt'),
        host='84.201.138.48',
        num_imports=10,
        num_citizens_in_import=10000,
    )
