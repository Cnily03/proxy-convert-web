from flask import Flask, request
from urllib.parse import urlparse
import socket
import ipaddress
import sys
import os
import argparse
from waitress import serve
from pclib.proxy.clash2singbox import clash2singbox


PRODUCTION = True
HOST = '0.0.0.0'
PORT = 5000
DEBUG = False


def parse_args():
    global PRODUCTION, HOST, PORT, DEBUG
    parser = argparse.ArgumentParser(description='Run the web server to convert proxy rules')
    parser.add_argument(
        '--production', action='store_true', required=False,
        help='Run in production mode (default)')
    parser.add_argument('-dev', '--development', action='store_true',
                        required=False, help='Run in development mode')
    parser.add_argument('-H', '--host', type=str, metavar="<host>", required=False,
                        help=f'Host to bind to (default: {HOST})')
    parser.add_argument('-p', '--port', type=int, metavar="<port>", required=False,
                        help=f'Port to bind to (default: {PORT})')
    parser.add_argument('--debug', action='store_true', required=False, help='Run in debug mode')

    args = parser.parse_args()

    if args.production:
        PRODUCTION = True
    elif args.development:
        PRODUCTION = False
    if args.host:
        HOST = args.host
    if args.port:
        PORT = args.port
    if args.debug:
        DEBUG = True


app = Flask(__name__)


def project_root():
    return os.path.abspath(os.path.dirname(__file__))


def url_not_pri(url):
    try:
        host = urlparse(url).hostname
        ip = socket.gethostbyname(host)

        if ipaddress.ip_address(ip).is_private:
            return False

    except:
        # except ValueError:
        return False

    return True


def waf_url(url):
    if url == None:
        return None
    if url.startswith('http://') or url.startswith('https://'):
        if url_not_pri(url):
            return url
        else:
            return None
    else:
        return None


def error_json(code, message):
    return {
        'code': code,
        'error': message
    }


@app.route('/clash', methods=['GET'])
def clash():
    params = request.args
    url = params.get('url', type=str)
    target = params.get('target', type=str)
    url = waf_url(url)
    try:
        if url == None:
            return error_json(400, 'Invalid Parameter: url'), 400
        if target == 'singbox':
            return clash2singbox(url, bin_dir=os.path.join(project_root(), 'bin'))
        else:
            return error_json(400, 'Invalid Parameter: target'), 400
    except Exception as e:
        print("\033[31mError:\033[0m", e, file=sys.stderr)
        return error_json(500, 'Internal Server Error'), 500


if __name__ == '__main__':
    parse_args()
    if not PRODUCTION:
        print('Running in development mode...')
        if HOST != '0.0.0.0':
            print("\033[33mWarning:\033[0m", f"Host {HOST} is not affected in development mode")
        app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
    else:
        print('Running in production mode...')
        print(f'Binding to http://{"localhost" if HOST == "0.0.0.0" else HOST}:{PORT}')
        serve(app, host=HOST, port=PORT)
