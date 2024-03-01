import os
import json
import hashlib
from base64 import b64encode, b64decode
from pulib.utils import waf_url, error_json, project_root, unique_list
import yaml
import requests


def safe_url(url):
    # replace " { }
    return url.replace('"', '%22').replace('{', '%7B').replace('}', '%7D')


RULES_PREDIFINED = {
    "default": [
        "DOMAIN-SUFFIX,local,DIRECT",
        "DOMAIN-SUFFIX,lan,DIRECT"
    ]
}


def clash_rules(params):
    # check params
    inject_arr = []
    # - url
    url = waf_url(params['url'])
    if url == None:
        return error_json(400, 'Invalid URL')
    # - use (optional)
    if 'use' in params:
        inject_predefined_keys = [t.strip() for t in params['use'].split(',')]
        for key in inject_predefined_keys:
            if key not in RULES_PREDIFINED:
                return error_json(400, 'Invalid key: {0}'.format(key))
            inject_arr.extend(RULES_PREDIFINED[key])
        del inject_predefined_keys
    # - custom (optional)
    if 'custom' in params:
        inject_json_text = b64decode(params['custom']).decode(encoding='utf-8')
        try:
            inject_json = json.loads(inject_json_text)
            if isinstance(inject_json, list):
                for rule in inject_json:
                    if not isinstance(rule, str):
                        return error_json(400, 'Meet non-string rule in custom rules')
                    inject_arr.append(rule)
        except:
            return error_json(400, 'Invalid JSON')
        del inject_json_text
    # download and inject
    content = requests.get(url).text
    yaml_obj = yaml.safe_load(content)
    del content
    if 'rules' not in yaml_obj:
        yaml_obj['rules'] = inject_arr
    else:
        yaml_obj['rules'] = unique_list(inject_arr + yaml_obj['rules'])
    return yaml.dump(yaml_obj, allow_unicode=True, width=-1), 'text/plain'
