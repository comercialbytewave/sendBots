#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_SOURCE="$ROOT_DIR/dist/SendBots"
INSTALL_DIR="$HOME/.local/opt/sendbots"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

if [[ ! -x "$APP_SOURCE/SendBots" ]]; then
  echo "Executavel Linux nao encontrado em: $APP_SOURCE/SendBots"
  echo "Execute primeiro: ./scripts/build_linux.sh"
  exit 1
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR"
rm -rf "$INSTALL_DIR"
cp -R "$APP_SOURCE" "$INSTALL_DIR"

cat > "$BIN_DIR/sendbots" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/SendBots" "\$@"
EOF
chmod +x "$BIN_DIR/sendbots"

cat > "$DESKTOP_DIR/sendbots.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=SendBots
Comment=Envio de notas fiscais e boletos via AlowChat
Exec=$INSTALL_DIR/SendBots
Terminal=false
Categories=Office;Utility;
EOF

chmod +x "$DESKTOP_DIR/sendbots.desktop"

echo "SendBots instalado em: $INSTALL_DIR"
echo "Atalho criado em: $DESKTOP_DIR/sendbots.desktop"
echo "Comando disponivel: sendbots"

