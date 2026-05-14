#!/bin/bash
# ─────────────────────────────────────────────────────
#  PoP Monitor — Instalador automático (Linux/macOS)
#  Uso: ./instalar.sh
# ─────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         PoP Monitor — Instalação automática          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Verifica Python
if ! command -v python3 &>/dev/null; then
  echo "✗ Python3 não encontrado. Instale em: https://python.org"
  exit 1
fi
echo "✔ Python3 encontrado: $(python3 --version)"

# Cria o venv
echo "► Criando ambiente virtual..."
python3 -m venv "$VENV"
source "$VENV/bin/activate"

# Instala dependências
echo "► Instalando dependências..."
pip install -r "$SCRIPT_DIR/requirements.txt" -q
echo "✔ Dependências instaladas"

# Descobre o IP local
IP=$(python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8',80))
print(s.getsockname()[0])
s.close()
" 2>/dev/null || echo "127.0.0.1")

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║           PoP Monitor — Instalado!                   ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Local  →  http://localhost:5050                     ║"
printf "║  Rede   →  http://%-34s║\n" "$IP:5050"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Iniciando o dashboard...                            ║"
echo "║  Pressione Ctrl+C para encerrar                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Abre o navegador
sleep 1 && (xdg-open "http://localhost:5050" 2>/dev/null || open "http://localhost:5050" 2>/dev/null) &

# Inicia a API
python3 "$SCRIPT_DIR/pop_monitor_api.py"
