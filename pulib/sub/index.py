import requests
import sys
import yaml
from pulib.utils import error_json, unique_list, register_sub, waf_url, YAMLPiper
from pulib.mod.clash import ClashMod as mod


@register_sub(identifier='index')
def main(path: str, search: str, params: dict):
    # get content
    sub_uri = waf_url(params.get('url', None))
    if sub_uri is None:
        return error_json(400, 'Invalid Parameter: url'), 400
    sub_type = params.get('type', None)
    content = ""
    try:
        resp = requests.get(sub_uri)
        if resp.status_code != 200:
            return error_json(500, 'Remote Server Error'), 500
        content = resp.text
        del resp
    except TimeoutError:
        return error_json(500, 'Remote Server Timeout'), 500
    except Exception as e:
        return error_json(500, 'Remote Server Error'), 500

    if sub_type is None:
        return content, 'text/plain'

    enable_mods = params.get('mod', '').split(',')
    enable_mods = [x.strip() for x in enable_mods if x.strip()]

    def apply_mod(mod_name, func):
        if mod_name in enable_mods:
            return func
        else:
            return None

    if sub_type == 'clash':

        # parse
        yaml_obj = yaml.safe_load(content)
        del content
        proxy_yaml = YAMLPiper(yaml_obj)

        # process
        proxy_yaml.sequential(
            apply_mod('local', mod.rules.local),
        )

        # return
        return yaml.dump(yaml_obj, allow_unicode=True, width=-1), 'text/plain'

    else:
        return error_json(400, 'Unknown Parameter Value: type'), 400
