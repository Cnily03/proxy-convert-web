import os
import sys
import hashlib

def safe_url(url):
    # replace " { }
    return url.replace('"', '%22').replace('{', '%7B').replace('}', '%7D')

def clash2singbox(url, bin_dir):
    os.makedirs('/tmp/clash2singbox', exist_ok=True)
    url_sha128 = hashlib.sha1(url.encode()).hexdigest()
    fp="/tmp/clash2singbox/" + url_sha128
    # run command
    bin_dir = os.path.abspath(bin_dir)
    bin_path = os.path.join(bin_dir, 'clash2singbox')
    os.system(bin_path + ' -url "' + safe_url(url) + '" -o ' + fp)
    # read result
    file=open(fp, 'r')
    return file.read()