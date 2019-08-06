from aiohttp import web

from citizens.api import (
    new_import, update_citizen, get_citizens, get_presents_by_month
)
from citizens.storage import MongoStorage


def get_app():
    app = web.Application()
    app.storage = MongoStorage({'db': 'citizens'})
    app.add_routes([
        web.post('/imports', new_import),
        web.patch(r'/imports/{import_id:\d+}/citizens/{citizen_id:\d+}', update_citizen),
        web.get(r'/imports/{import_id:\d+}/citizens', get_citizens),
        web.get(r'/imports/{import_id:\d+}/citizens/birthdays', get_presents_by_month)
    ])
    return app


if __name__ == '__main__':
    app = get_app()
    web.run_app(app, port=8888)
