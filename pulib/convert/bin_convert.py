import os
import hashlib
from pulib.utils import waf_url, error_json, project_root


def safe_url(url):
    # replace " { }
    return url.replace('"', '%22').replace('{', '%7B').replace('}', '%7D')


def clash2singbox(params):
    # check params
    url = waf_url(params['url'])
    if url == None:
        return error_json(400, 'Invalid URL')
    # prepare environment
    os.makedirs('/tmp/clash2singbox', exist_ok=True)
    url_sha128 = hashlib.sha1(url.encode()).hexdigest()
    fp = "/tmp/clash2singbox/" + url_sha128
    # run command
    bin_path = os.path.join(project_root("bin"), 'convert.clash-singbox')
    os.system(bin_path + ' -url "' + safe_url(url) + '" -o ' + fp)
    # read result
    result = open(fp, 'r').read()
    os.remove(fp)
    return result, 'application/json'
