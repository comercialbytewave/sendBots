#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m pip install --upgrade pyinstaller pypdf pystray Pillow
pyinstaller packaging/sendbots.spec

mkdir -p dist/linux
tar -C dist -czf dist/linux/SendBots-linux.tar.gz SendBots

echo "Build Linux concluido:"
echo "  dist/SendBots/SendBots"
echo "  dist/linux/SendBots-linux.tar.gz"
echo
echo "Para instalar localmente:"
echo "  ./scripts/install_linux.sh"
