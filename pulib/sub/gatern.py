import requests
import sys
import yaml
from pulib.utils import error_json, unique_list, register_sub


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


class mod:
    class rules:
        def local(yaml_obj):
            inject_rules = [
                "DOMAIN-SUFFIX,lan,DIRECT",
            ]
            yaml_obj["rules"] = unique_list(inject_rules + yaml_obj["rules"])


@register_sub(identifier='gatern')
def main(path: str, search: str, params: dict):
    print(search)
    # get content
    sub_uri = "https://sub.gt-up.com/app/{0}{1}"
    sub_uri = sub_uri.format(path, search)
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

    if path.startswith('clash/'):

        # parse
        yaml_obj = yaml.safe_load(content)
        del content
        proxy_yaml = YAMLPiper(yaml_obj)

        # process
        proxy_yaml.sequential(
            mod.rules.local,
        )

        # return
        return yaml.dump(yaml_obj, allow_unicode=True, width=-1), 'text/plain'

    else:
        return content, 'text/plain'
