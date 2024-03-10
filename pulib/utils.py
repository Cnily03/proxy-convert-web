from urllib.parse import urlparse
import socket
import ipaddress
import os


def project_root(fn=''):
    file_dir = os.path.abspath(os.path.dirname(__file__))
    prj_dir = os.path.abspath(os.path.dirname(file_dir))
    if fn:
        return os.path.join(prj_dir, fn)
    return prj_dir


def unique_list(seq):
    seen = set()
    return [x for x in seq if x.__hash__ == None or not (x in seen or seen.add(x))]


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


def safe_fn(fn):
    return fn.replace(r'[ _-.\/\\]', '_').replace(r'[^a-zA-Z0-9_]', '')


def waf_url(url):
    if url == None:
        return None
    protocol = urlparse(url).scheme
    if protocol == 'http' or protocol == 'https':
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


SUB_FUNCS = {}


def register_sub(identifier):
    """Register a function as a subscription processor.
    """
    def decorator(func):
        SUB_FUNCS[identifier] = func
        return func
    return decorator

class YAMLPiper:
    def __init__(self, yaml_obj):
        self.yaml_obj = yaml_obj

    def pipe(self, func):
        func(self.yaml_obj)
        return self

    def sequential(self, *funcs):
        for func in funcs:
            if callable(func):
                self.pipe(func)
        return self

    def get(self):
        return self.yaml_obj