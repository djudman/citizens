import asyncio
import json
import logging
import logging.config
import os
import socket
from os import makedirs
from os.path import realpath, dirname, expanduser, join, exists

from aiohttp import web
from aiojobs.aiohttp import setup

from citizens.data import DataValidationError
from citizens.api import (
    new_import, update_citizen, get_citizens, get_presents_by_month,
    get_age_percentiles
)
from citizens.storage import MongoStorage, AsyncMongoStorage


@web.middleware
async def errors_middleware(request, handler):

    def log_error(request, exception):
        message = '`{0} {1}` failed. {2}'.format(request.method, request.url, exception)
        request.app.logger.error(message, exc_info=True)

    try:
        response = await handler(request)
    except DataValidationError as e:
        log_error(request, e)
        raise web.HTTPBadRequest()
    except Exception as e:
        log_error(request, e)
        raise
    return response


async def shutdown(app):
    await app.storage.close()


class CitizensRestApi:
    def __init__(self):
        self._unix_socket = None
        self._logger = logging.getLogger('citizens')
        self._config = self._load_config()
        self._app = self._create_app()

    def _load_config(self):  # TODO: сделать лучше
        filename = 'citizens.config.json'
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

    def _create_app(self):
        # TODO: здесь нужен new_event_loop() для случая, когда используем из кода 
        # и хотим запускать и останавливать приложение несколько раз
        # Надо разрулить с тестами

        # loop = asyncio.get_event_loop()
        # asyncio.set_event_loop(loop)
        app = web.Application(
            # loop=loop,
            logger=logging.getLogger('citizens'),
            middlewares=[errors_middleware],
            client_max_size=1024 ** 3 * 2,  # 2Gb
        )
        setup(app)
        app.storage = AsyncMongoStorage({'db': 'citizens'})
        app.add_routes([
            web.post('/imports', new_import),
            web.patch(r'/imports/{import_id:\d+}/citizens/{citizen_id:\d+}', update_citizen),
            web.get(r'/imports/{import_id:\d+}/citizens', get_citizens),
            web.get(r'/imports/{import_id:\d+}/citizens/birthdays', get_presents_by_month),
            web.get(r'/imports/{import_id:\d+}/towns/stat/percentile/age', get_age_percentiles),
        ])
        app.on_cleanup.append(self._shutdown)
        return app

    def run(self, host='127.0.0.1', port=8080, unix_socket_path=None):
        sock = None
        endpoint_name = None
        if unix_socket_path is not None:
            host = None
            port = None
            socket_dirpath = realpath(dirname(unix_socket_path))
            if not exists(socket_dirpath):
                os.makedirs(socket_dirpath, exist_ok=True)
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(unix_socket_path)
            self._unix_socket = (unix_socket_path, sock)
            self._logger.info(f'Unix socket `{unix_socket_path}` is ready.')
            endpoint_name = unix_socket_path
        else:
            endpoint_name = f'{host}:{port}'
        self._logger.info(f'Starting application on {endpoint_name}')
        web.run_app(self._app, print=None, host=host, port=port, sock=sock)

    async def _shutdown(self, app):
        await app.storage.close()
        if self._unix_socket is not None:
            filepath, sock = self._unix_socket
            if sock.fileno() != -1:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                self._logger.info(f'Unix socket `{filepath}` closed.')
            if exists(filepath):
                os.unlink(filepath)
                self._logger.info(f'File `{filepath}` deleted.')
        self._logger.info('Application is shutdown.')
