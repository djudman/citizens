import argparse
import os
import socket
import sys
from os.path import dirname, realpath, exists

from aiohttp import web

project_dir = realpath(dirname(dirname(__file__)))
sys.path.insert(1, project_dir)

from citizens.app import create_app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Citizens REST API")
    parser.add_argument('--socket')
    parser.add_argument('--port')
    args = parser.parse_args()

    sock = None
    if args.socket:
        socket_dirpath = realpath(dirname(args.socket))
        if not exists(socket_dirpath):
            os.makedirs(socket_dirpath, exist_ok=True)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(args.socket)

    app = create_app()
    port = args.port or 8080
    web.run_app(app, port=port, sock=sock)
