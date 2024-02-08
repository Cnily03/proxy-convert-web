# Proxy Convert (Web)

Rhe web server to convert proxy rules.

## Usage

This web server is running on Unix-like systems.

Get a bin file named `from2to` and put it in `bin` directory.

For example, for converting clash rules to singbox rules, you should get the bin file from [clash2singbox](https://github.com/xmdhs/clash2singbox), then rename it to `clash2singbox` and put it in `bin` directory.

Run `install.sh` for 64-bit system to get all the supported bin files.

In another way, you can get the bin file according to the following list.

- Clash -> Singbox: [clash2singbox](https://github.com/xmdhs/clash2singbox)

Install the required packages.

```shell
pip install -r requirements.txt
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

## License

CopyRight (c) Cnily03. All rights reserved.

Licensed under the [MIT](https://github.com/Cnily03/proxy-convert-web/blob/main/LICENSE) License.
