import asyncio
import json
import logging
import logging.config
import os
import socket
from contextlib import contextmanager
from os.path import realpath, dirname, expanduser, join, exists

from aiohttp import web
from aiojobs.aiohttp import setup as aiojobs_setup

from citizens.api import (
    CitizensBadRequest, new_import, update_citizen, get_citizens,
    get_presents_by_month, get_age_percentiles
)
from citizens.storage import AsyncMongoStorage, ImportNotFound


@contextmanager
def cd(dirpath):
    prevdir = os.getcwd()
    os.chdir(expanduser(dirpath))
    try:
        yield
    finally:
        os.chdir(prevdir)


@web.middleware
async def errors_middleware(request, handler):
    try:
        response = await handler(request)
    except Exception as e:
        message = '`{0} {1}` failed. {2}'.format(request.method, request.url, e)
        request.app.logger.error(message, exc_info=True)
        if type(e) in (CitizensBadRequest, ImportNotFound):
            raise web.HTTPBadRequest()
        raise
    return response


# NOTE: используется только если в конфиге выставлен `debug: true`
@web.middleware
async def logging_middleware(request, handler):
    import hashlib
    import time
    import random
    import sys

    logger = request.app.logger
    request_id = '{0}{1}{2}{3}'.format(time.time(), request.method, request.url,
                                       random.randint(0, sys.maxsize)).encode()
    request_id = hashlib.sha256(request_id).hexdigest()[:10]
    logger.debug('> [{0}] {1} {2}'.format(request_id, request.method, request.url))
    response = await handler(request)
    status = '{0} {1}'.format(response.status, response.reason)
    logger.debug('< [{0}] {1} {2}'.format(request_id, status, response.body[:50]))
    return response


class CitizensRestApi:
    def __init__(self):
        self._logger = logging.getLogger('citizens')
        config_filepath = join(dirname(dirname(__file__)), 'citizens.config.json')
        self._config = self._load_config(config_filepath)
        self._unix_socket = None
        self._app = self._create_app()

    def _load_config(self, filepath):
        if not exists(filepath):
            self._logger.warning(f'Config file `{filepath}` not found. Loaded default config.')
            return {
                'logging': {'version': 1},
                'storage': {'db': 'test', 'connection_string': 'localhost'},
            }
        config_dir = realpath(dirname(filepath))
        with cd(config_dir):  # чтобы относительные пути в конфиге были относительно самого конфига
            with open(filepath) as f:
                config = json.load(f)
            logging_config = config['logging']
            log_filename = logging_config['handlers']['citizens_file']['filename']
            log_dir = realpath(dirname(log_filename))
            if not exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            logging.config.dictConfig(logging_config)
        self._logger.info(f'Loaded config {filepath}.')
        return config

    def _create_app(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client_body_max_size = self._config.get('client_body_max_size', 1024 ** 2)
        middlewares = [errors_middleware]
        if self._config.get('debug'):
            middlewares.append(logging_middleware)
        app = web.Application(logger=self._logger, middlewares=middlewares, client_max_size=client_body_max_size)
        aiojobs_setup(app)
        storage_config = self._config['storage']
        # TODO: тут можно брать класс из конфига и создавать обект указанного в конфиге класса
        app.storage = AsyncMongoStorage(storage_config)
        app.add_routes([
            web.post('/imports', new_import),
            web.patch(r'/imports/{import_id:\d+}/citizens/{citizen_id:\d+}', update_citizen),
            web.get(r'/imports/{import_id:\d+}/citizens', get_citizens),
            web.get(r'/imports/{import_id:\d+}/citizens/birthdays', get_presents_by_month),
            web.get(r'/imports/{import_id:\d+}/towns/stat/percentile/age', get_age_percentiles),
        ])
        app.on_shutdown.append(self._shutdown)
        return app

    def run(self, host='localhost', port=8080, unix_socket_path=None):
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
