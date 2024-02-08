#!/bin/bash

project_root=$(realpath `dirname $0`)

curl https://github.com/xmdhs/clash2singbox/releases/download/v0.0.2/clash2singbox-linux-amd64 -o $project_root/bin/clash2singbox