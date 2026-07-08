#!/usr/bin/env bash
set -euo pipefail

rm -rf "$HOME/.local/opt/sendbots"
rm -f "$HOME/.local/bin/sendbots"
rm -f "$HOME/.local/share/applications/sendbots.desktop"

echo "SendBots removido do usuario atual."
echo "Configuracoes, historico e logs foram mantidos em ~/.local/share/sendbots."

