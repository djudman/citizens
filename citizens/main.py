import json
import logging
import logging.config
import os
from os import makedirs
from os.path import realpath, dirname, expanduser, join, exists

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
        request.app.logger.error(e, exc_info=True)
        raise web.HTTPBadRequest()
    except Exception as e:
        request.app.logger.error(e, exc_info=True)
        raise web.HTTPInternalServerError()
    return response


async def shutdown(app):
    app.storage.close()


def load_config():  # TODO: сделать лучше
    filename = 'citizens.json'
    search_path = (dirname(dirname(__file__)), '~', '~/.config')
    for dir_name in search_path:
        filepath = join(realpath(expanduser(dir_name)), filename)
        if exists(filepath):
            work_dir = os.getcwd()
            os.chdir(realpath(dirname(filepath)))
            # TODO: контекстный менеджер про "перейти в директорию с конфигом"
            with open(filepath) as f:
                config = json.load(f)
                log_dir = realpath(dirname(config['logging']['handlers']['citizens_file']['filename']))
                if not exists(log_dir):
                    makedirs(log_dir, exist_ok=True)
                logging.config.dictConfig(config['logging'])
                os.chdir(work_dir)
                return config
    return {
        'logging': {'version': 1},
    }


def create_app():
    load_config()
    app = web.Application(
        logger=logging.getLogger('citizens'),
        middlewares=[errors_middleware]
    )
    app.storage = MongoStorage({'db': 'citizens'})
    app.add_routes([
        web.post('/imports', new_import),
        web.patch(r'/imports/{import_id:\d+}/citizens/{citizen_id:\d+}', update_citizen),
        web.get(r'/imports/{import_id:\d+}/citizens', get_citizens),
        web.get(r'/imports/{import_id:\d+}/citizens/birthdays', get_presents_by_month),
        web.get(r'/imports/{import_id:\d+}/towns/stat/percentile/age', get_age_percentiles),
    ])
    return app


if __name__ == '__main__':
    app = create_app()
    app.on_cleanup.append(shutdown)
    web.run_app(app, port=8888)
