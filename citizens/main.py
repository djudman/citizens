from aiohttp import web

from citizens.api import new_import
from citizens.storage import Storage


app = web.Application()
app.storage = Storage({'db': 'citizens'})
app.add_routes([
    web.post('/imports', new_import)
])
web.run_app(app, port=8888)
