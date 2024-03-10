# Proxy Utils - Web

The web server to process proxy rules.

## Installation

### From Source

This web server is running on Unix-like systems.

Install the required packages.

```shell
pip install -r requirements.txt
```

The `bin/` directory is used to store the binary files for some functions. Here is the list of binary file names and their references.

- [convert.clash-singbox](https://github.com/xmdhs/clash2singbox)

You can install them by running `install.sh` (sudo), or with option `--force` to overwrite the existing files.

```shell
sudo bash ./install.sh
```

Start the web server on production mode.

```python
python web.py
```

Fore more options, please run with `--help`.

```plain
options:
  -h, --help            show this help message and exit
  --production          Run in production mode (default)
  -dev, --development   Run in development mode
  -H <host>, --host <host>
                        Host to bind to (default: 0.0.0.0)
  -p <port>, --port <port>
                        Port to bind to (default: 5000)
  --debug               Run in debug mode
```

Or you can modify `config.yml` to change the default configuration.

### From Docker

You can also run this web server in a docker container.

For docker compose, run the following command at the root of the project.

```shell
docker compose up -d
```

Or you can build and run the docker container manually. Change `5000` after `-p` into the port to visit.

```shell
docker build -t proxy-utils-web:latest .
docker run -d --restart=unless-stopped -v '.:/app' -p '5000:80' --name proxy-web proxy-utils-web:latest
```

You can specify envrionment variables to change the default configuration in `config.yml`.

```shell
docker run -d \
    --restart=unless-stopped \
    -v '.:/app' \
    -p '5000:80' \
    -e RUN_ENV=development \
    -e DEBUG=true \
    --name proxy-web \
    proxy-utils-web:latest
```

> [!NOTE]
> The port is `80` and the host is `0.0.0.0` in the container and cannot be changed unless you modify `docker.sh`.

## Routes

> [!TIP]
> Marked 🔹 for required, marked 🔸 for optional

- `/convert?source=<source>&target=<target>&[...args]` \
  Convert the proxy rules from the source to the target.
  - `source`: The source proxy rules format.
  - `target`: The target proxy rules format.
  - `[...args]`: The arguments for the convert function.

  <p><details>
    <summary><strong>Implementations</strong></summary><p>

  **Example:** `/convert?source=clash&target=singbox&url=http://xxx`

  | source | target | url | Description |
  | ------ | ------ | --- | ---------------- |
  | 🔹 `clash` | 🔹 `singbox` | 🔹 Subscription URL | Convert Clash rules to Singbox rules. |

  </p></details></p>

- `/apply?rule=<rule>&[...args]` \
  Apply a rule to the proxy rules.
  - `rule`: The rule to apply.
  - `[...args]`: The arguments for the rule function.

  <p><details>
    <summary><strong>Implementations</strong></summary><p>

  **Example:** `/apply?rule=inject.clash.rules&url=http://xxx>&use=default&custom=WyJET01BSU4tU1VGRklYLGdvb2dsZS5jb20sRElSRUNUIl0%3D`

  ```javascript
  urlencode(base64('["DOMAIN-SUFFIX,google.com,DIRECT"]')) == 'WyJET01BSU4tU1VGRklYLGdvb2dsZS5jb20sRElSRUNUIl0%3D'
  ```

  | rule | url | use | custom | Description |
  | ---- | --- | --- | ------ | ---------------- |
  | 🔹 `inject.clash.rules` | 🔹 Subscription URL | 🔸 `default`, joined with `,` | 🔸 base64 encoded JSON array string of custom rules | Inject rules into Clash rules. |

  </p></details></p>

- `/sub/:identifier/:path` \
  Custom subsciption route.
  - `identifier`: The identifier of the subscription
  - `path`: Remaining url path

  <p><details>
    <summary><strong>Implementations</strong></summary><p>

  **Example:** `/sub/gatern/clash/xxx/xxx?mod=local`

  </p></details></p>

- `/sub?url=<URL>&[...args]` \
  A special route of `/sub/:identifier/:path`. Apply mods to a subscription.
  - `url`: Subscription URL

  <p><details>
    <summary><strong>Implementations</strong></summary><p>

  **Example:** `/sub?url=http://xxx&type=clash&mod=local`

  | url | mod | type | Description |
  | --- | --- | ---- | ---------------- |
  | 🔹 Subscription URL | 🔸 `local`, joined with `,` | 🔸 `clash` | Apply mods to a subscription. |

  </p></details></p>

## Development

### Customize Subscription Processor

Create or edit python files in the directory `pulib/sub/` to process your subscription.

The processor function receives 3 arguments:

- `path` (str) \
  The path of the URL (same as in route `/sub/:identifier/:path`).
- `search` (str) \
  The search part of the URL.
- `params` (dict) \
  The dict of query parameters of the URL.

The processor has optional return types:

- `{"code": int, "message": str}`  \
  A dict (json) to response, status same as `code`.
- `{"code": int, "message": str}, status_code` \
  A tuple with a dict (json) to response and response status code.
- `(content: str | bytes, mimetype: str)` \
  A tuple with response data and its mimetype.

Use decorator `@register_sub(identifier='...')` to register your processor function.

> [!IMPORTANT]
> Remember that `identifier` should be unique and cannot be started with `_`.
> If `identifier` is `index`, the route becomes `/sub`, and `path` is empty string.
> In case that the route is `/sub/:identifier` or `/sub/:identifier/`, `path` is delivered as empty string.

#### Example

```python
from pulib.utils import register_sub
import requests

@register_sub(identifier='gatern')
def main(path: str, search: str, params: dict):
    try:
        content = requests.get(f'http://xxx/{path}{search}').content
        return content, 'text/plain'
    except Exception as e:
        return {"code": 500, "message": "Internal Server Error"}, 500
```

> [!TIP]
> You can import `error_json` from `pulib.utils` to simplify the error response.
> ```python
> from pulib.utils import error_json
> ...
>   except Exception as e:
>       return error_json(500, "Internal Server Error"), 500
> ```
> There are other useful utilities in `pulib.utils` to help you program.

## Campus Network Injection

### Proxy Transformation

Here is an example of how to inject EasyConnect proxy rules into Clash proxy rules, in order to visit the campus network everywhere Internet is available.

You need a public approchable linux server armed with docker.

Download [this script](https://gist.github.com/Cnily03/cb286a2034b27630838a301b4f3bdcff) to `/usr/bin` (or any other directory in PATH), and make it executable by running `chmod +x /usr/bin/easyvpn`.

Then you can convert EasyConnect into Socks5 or HTTP proxy. Try `easyvpn --help` for help.

Finally, expose corresponding ports on your server.

### Modify your subscription rules

Referring to [# Customize Subscription Processor](#customize-subscription-processor) or lookup `pulib/sub/index.py` to know how to handle custom rule injection. You can import `YAMLPiper` from `pulib.utils` to make the injection more easily.

For example, if your subcription is for clash, modify `pulib/mod/clash.py`

```python
class ClashMod:
    class proxy:
        def school(yaml_obj):
            inject_proxies = [{
                "name": "EasyConnect",
                "type": "socks5",
                "server": "SERVER WHO TRANSFORMS EASYCONNECT",
                "port": 10800,
                "username": "YOUR SOCKS5 USERNAME",
                "password": "YOUR SOCKS5 PASSWORD",
                "network": "tcp",
            }]
            inject_proxy_groups = [{
                "name": "SCHOOL",
                "type": "select",
                "proxies": ["EasyConnect"]
            }]
            inject_rules = [
                "DOMAIN,any.school.edu.cn,SCHOOL"
            ]
            yaml_obj["proxies"] = unique_list(yaml_obj["proxies"] + inject_proxies)
            yaml_obj["proxy-groups"] = unique_list(yaml_obj["proxy-groups"] + inject_proxy_groups)
            yaml_obj["rules"] = unique_list(inject_rules + yaml_obj["rules"])
```

Then modify `pulib/sub/index.py` or your customized file. Apply `ClashMod.proxy.school` to mod.

```python
proxy_yaml.sequential(
    apply_mod('campus', ClashMod.proxy.school),
    ...
)
```

Then in the route, deliver `mod=campus` in URL parameters to inject rules defined in `ClashMod.proxy.school`.

## License

CopyRight (c) Cnily03. All rights reserved.

Licensed under the [MIT](https://github.com/Cnily03/proxy-convert-web/blob/main/LICENSE) License.
