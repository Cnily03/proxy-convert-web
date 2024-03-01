import traceback
from flask import Flask, Response, json, request
from werkzeug.serving import WSGIRequestHandler
from werkzeug._internal import _log as werkzeug_log
import logging
import sys
import argparse
import yaml
from waitress import serve
import pulib.convert as pu_convert
import pulib.apply as pu_apply
import pulib.sub as pu_sub
from pulib.utils import error_json, project_root

CONFIG = yaml.safe_load(open(project_root('config.yml'), 'r'))

VERSION = CONFIG['version']

PRODUCTION = CONFIG['enviroment'] != 'development'
HOST = CONFIG['host']
PORT = CONFIG['port']
DEBUG = CONFIG['debug']


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
    parser.add_argument('--debug', action='store_true', required=False,
                        help=f'Run in debug mode (default: {DEBUG})')

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


def map_convert_func(p_source, p_target):
    if p_source == 'clash' and p_target == 'singbox':
        return pu_convert.clash2singbox
    else:
        return None


def map_apply_func(p_rule):
    if p_rule == 'convert.clash-singbox':
        return pu_convert.clash2singbox
    if p_rule == 'inject.clash.rules':
        return pu_apply.inject.clash_rules
    else:
        return None


def map_sub_func(identifier):
    all_func = [attr for attr in dir(pu_sub) if not attr.startswith('_')]
    if identifier not in all_func:
        return None
    else:
        return getattr(pu_sub, identifier)


@app.route('/convert', methods=['GET'])
def route_convert():
    params = request.args
    required_params = ['source', 'target']

    p_source = params.get('source', type=str)
    p_target = params.get('target', type=str)
    other_params = {k: v for k, v in params.items() if k not in required_params}

    missing_params = [p for p in required_params if p not in params]
    if len(missing_params) > 0:
        return error_json(400, f'Missing parameters: {", ".join(missing_params)}'), 400

    try:
        convert_func = map_convert_func(p_source, p_target)
        if callable(convert_func):
            # call function
            r = convert_func(other_params)
            t = r if isinstance(r, tuple) else (r, None)
            if isinstance(t[0], dict) and 'error' in t[0]:
                (resp, status_code) = t[0], t[1]
                if not isinstance(status_code, int) and 'code' in resp:
                    status_code = int(resp['code'])
                if not isinstance(status_code, int):
                    status_code = 500
                return Response(json.dumps(resp),
                                status=status_code, mimetype="application/json")
            else:
                (resp, mimetype) = t
                return resp if mimetype is None else Response(str(resp), mimetype=mimetype)
        else:
            return error_json(400, 'Invalid Chain: {0} -> {1}'.format(p_source, p_target)), 400
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        print("\033[31mError:\033[0m", e, file=sys.stderr)
        return error_json(500, 'Internal Server Error'), 500


@app.route('/apply', methods=['GET'])
def route_apply():
    params = request.args
    required_params = ['rule']

    p_rule = params.get('rule', type=str)
    other_params = {k: v for k, v in params.items() if k not in required_params}

    missing_params = [p for p in required_params if p not in params]
    if len(missing_params) > 0:
        return error_json(400, f'Missing parameters: {", ".join(missing_params)}'), 400

    try:
        rule_func = map_apply_func(p_rule)
        if callable(rule_func):
            # call function
            r = rule_func(other_params)
            t = r if isinstance(r, tuple) else (r, None)
            if isinstance(t[0], dict) and 'error' in t[0]:
                (resp, status_code) = t[0], t[1]
                if not isinstance(status_code, int) and 'code' in resp:
                    status_code = int(resp['code'])
                if not isinstance(status_code, int):
                    status_code = 500
                return Response(json.dumps(resp),
                                status=status_code, mimetype="application/json")
            else:
                (resp, mimetype) = t
                return resp if mimetype is None else Response(str(resp), mimetype=mimetype)
        else:
            return error_json(400, 'Invalid Rule: {0}'.format(p_rule)), 400
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        print("\033[31mError:\033[0m", e, file=sys.stderr)
        return error_json(500, 'Internal Server Error'), 500


@app.route('/sub/<identifier>/<path:fullpath>', methods=['GET'])
def route_subscribe(identifier, fullpath):
    params = request.args
    search_index = request.url.find('?')
    search = "" if search_index == -1 else request.url[search_index:]
    try:
        sub_func = map_sub_func(identifier)
        if callable(sub_func):
            # call function
            r = sub_func(fullpath, search, params)
            t = r if isinstance(r, tuple) else (r, None)
            if isinstance(t[0], dict) and 'error' in t[0]:
                (resp, status_code) = t[0], t[1]
                if not isinstance(status_code, int) and 'code' in resp:
                    status_code = int(resp['code'])
                if not isinstance(status_code, int):
                    status_code = 500
                return Response(json.dumps(resp),
                                status=status_code, mimetype="application/json")
            else:
                (resp, mimetype) = t
                return resp if mimetype is None else Response(str(resp), mimetype=mimetype)
        else:
            return error_json(400, 'Invalid Identifier: {0}'.format(identifier)), 400
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        print("\033[31mError:\033[0m", e, file=sys.stderr)
        return error_json(500, 'Internal Server Error'), 500


@app.route("/", methods=['GET'])
def route_index():
    return {
        "name": "Proxy Utils",
        "version": VERSION,
        "description": "A simple web server to convert and apply proxy rules"
    }


if __name__ == '__main__':
    parse_args()
    if not PRODUCTION:
        print('Running in development mode...')
        if HOST != '0.0.0.0':
            print("\033[33mWarning:\033[0m", f"Host {HOST} is not affected in development mode")
        app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
    else:
        # enable waitress output
        waitress_logger = logging.getLogger('waitress')
        waitress_logger.root.handlers.clear()
        waitress_logger.root.addHandler(logging.StreamHandler(sys.stdout))
        waitress_logger.root.setLevel(logging.INFO)

        # enable flask request log
        class RequestMiddleware(object):
            def __init__(self, app):
                self.app = app

            def __call__(self, environ, start_response):
                method = environ['REQUEST_METHOD']
                path = environ['PATH_INFO']
                if environ['QUERY_STRING']:
                    path = path + '?' + environ['QUERY_STRING']

                class wsgi_instance:
                    command = method
                    request_version = environ['SERVER_PROTOCOL']
                    requestline = f"{method} {path} {environ['SERVER_PROTOCOL']}"

                    def log(type: str, message: str, *args) -> None:
                        def address_string(): return environ['REMOTE_ADDR']
                        def log_date_time_string(): return WSGIRequestHandler.log_date_time_string(WSGIRequestHandler)
                        werkzeug_log(
                            type,
                            f"{address_string()} - - [{log_date_time_string()}] {message}\n",
                            *args,
                        )

                def _start_response(status, response_headers, exc_info=None):
                    code = str(status).split(' ')[0]
                    size = "-"
                    WSGIRequestHandler.log_request(wsgi_instance, code, size)
                    return start_response(status, response_headers, exc_info)
                return self.app(environ, _start_response)
        app.wsgi_app = RequestMiddleware(app.wsgi_app)

        # start server
        print('Running in production mode...')
        # print(f'Binding to http://{HOST}:{PORT}')
        serve(app, host=HOST, port=PORT)
