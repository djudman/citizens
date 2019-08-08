from aiohttp import web
from aiohttp.web import middleware

from citizens.data import DataValidationError
from citizens.api import (
    new_import, update_citizen, get_citizens, get_presents_by_month,
    get_age_percentiles
)
from citizens.storage import MongoStorage


@middleware
async def errors_middleware(request, handler):
    try:
        response = await handler(request)
    except DataValidationError as e:
        # TODO: log an exception to file
        raise web.HTTPBadRequest()
    except Exception as e:
        # TODO: log an exception to file
        raise web.HTTPInternalServerError()
    return response


def create_app():
    app = web.Application(middlewares=[errors_middleware])
    app.storage = MongoStorage({'db': 'citizens'})
    app.add_routes([
        web.post('/imports', new_import),
        web.patch(r'/imports/{import_id:\d+}/citizens/{citizen_id:\d+}', update_citizen),
        web.get(r'/imports/{import_id:\d+}/citizens', get_citizens),
        web.get(r'/imports/{import_id:\d+}/citizens/birthdays', get_presents_by_month),
        web.get(r'/imports/{import_id:\d+}/towns/stat/percentile/age', get_age_percentiles),
    ])
    return app


async def shutdown(app):
    app.storage.close()


if __name__ == '__main__':
    app = create_app()
    app.on_cleanup.append(shutdown)
    web.run_app(app, port=8888)
