import argparse
import pathlib
import sys

project_dir = str(pathlib.Path(__file__).parent.parent.resolve())
sys.path.insert(0, project_dir)

from citizens.app import CitizensRestApi


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Citizens REST API')
    parser.add_argument('--socket')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8080)
    args = parser.parse_args()
    if args.socket:
        CitizensRestApi().run(unix_socket_path=args.socket)
    else:
        CitizensRestApi().run(host=args.host, port=args.port)
