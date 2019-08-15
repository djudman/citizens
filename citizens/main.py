import argparse
import sys
from os.path import dirname, realpath

project_dir = realpath(dirname(dirname(__file__)))
sys.path.insert(1, project_dir)

from citizens.app import CitizensRestApi


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Citizens REST API")
    parser.add_argument('--socket')
    parser.add_argument('--host')
    parser.add_argument('--port')
    args = parser.parse_args()

    kwargs = {}
    if args.socket:
        kwargs['unix_socket_path'] = args.socket
    else:
        if args.host:
            kwargs['host'] = args.host
        if args.port:
            kwargs['port'] = args.port

    CitizensRestApi().run(**kwargs)
