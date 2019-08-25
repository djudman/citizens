import os
import shutil
from os.path import exists, join, dirname

from aiohttp import web


async def __shutdown(app):
    app.cache.close()


def citizens_cache_setup(app, max_size=10):
    app.cache = CitizensFileCache(max_size)
    app.on_shutdown.append(__shutdown)


def use_cache(cache_key):
    def _use_cache(handler):
        async def wrapper(request):
            if not hasattr(request.app, 'cache'):
                return await handler(request)
            import_id = int(request.match_info['import_id'])
            cache = request.app.cache
            cached_data = cache.get(import_id, cache_key)
            if cached_data:
                return web.Response(body=cached_data, content_type='application/json')
            else:
                response = await handler(request)
                cache.put(import_id, cache_key, response.body)
                return response
        return wrapper
    return _use_cache


def clear_cache(handler):
    async def wrapper(request):
        if not hasattr(request.app, 'cache'):
            return await handler(request)
        import_id = int(request.match_info['import_id'])
        response = await handler(request)
        cache = request.app.cache
        if cache:
            cache.clear(import_id)
        return response
    return wrapper


class CitizensFileCache:
    def __init__(self, max_size=10):
        self._max_size = max_size
        self._citizens_by_import = {}

    def _get_cache_path(self, import_id=None, key=None):
        cache_path = '/tmp/citizens.cache'
        if import_id is not None:
            cache_path = join(cache_path, str(import_id))
        if key is not None:
            cache_path = join(cache_path, key)
        return cache_path

    def put(self, import_id, key, data):
        filepath = self._get_cache_path(import_id, key)
        if exists(filepath):
            os.unlink(filepath)
        else:
            cache_dir = dirname(filepath)
            os.makedirs(cache_dir, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(data)

    def get(self, import_id, key):
        filepath = self._get_cache_path(import_id, key)
        if exists(filepath):
            with open(filepath, 'rb') as f:
                return f.read()
    
    def clear(self, import_id):
        import_cache_dir = self._get_cache_path(import_id)
        if exists(import_cache_dir):
            shutil.rmtree(import_cache_dir)

    def close(self):
        cache_dir = self._get_cache_path()
        if exists(cache_dir):
            shutil.rmtree(cache_dir)
