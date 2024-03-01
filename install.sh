#!/bin/bash

project_root=$(realpath `dirname $0`)
bin_dir="$project_root/bin"
mkdir -p "$bin_dir"

force_mode=0
while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)
            force_mode=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

tmp_dir="$(mktemp -d)"

function fetch_bin() {
    local bin_name="$1"
    local bin_url="$2"
    if [ ! -f "$bin_dir/$bin_name" ] || [ "$force_mode" == "1" ]; then
        local tmp_path="$tmp_dir/$bin_name"
        echo "Fetching $bin_name ..."
        if curl -L -k "$bin_url" -o "$tmp_path" 2>/dev/null; then
            mv -Tf "$tmp_path" "$bin_dir/$bin_name" && \
            chmod +x "$bin_dir/$bin_name"
        else
            echo "Failed to fetch $bin_name"
        fi
    fi

}

fetch_bin "convert.clash-singbox" "https://github.com/xmdhs/clash2singbox/releases/download/v0.0.2/clash2singbox-linux-amd64"

# chmod +x "$bin_dir/*"
chmod -x "$bin_dir/.gitkeep"

rm -rf "$tmp_dir"