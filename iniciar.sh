#!/bin/bash
# ─────────────────────────────────────────────────────
#  PoP Monitor — Inicializador
#  Uso: ./iniciar.sh
# ─────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

# Cria o venv se não existir
if [ ! -d "$VENV" ]; then
  echo "► Criando ambiente virtual..."
  python3 -m venv "$VENV"
fi

# Ativa o venv
source "$VENV/bin/activate"

# Instala dependências se necessário
pip show flask >/dev/null 2>&1 || pip install -r "$SCRIPT_DIR/requirements.txt" -q

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
echo "║           PoP Monitor — em execução                  ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Local  →  http://localhost:5050                     ║"
printf "║  Rede   →  http://%-34s║\n" "$IP:5050"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Compartilhe o link 'Rede' com técnicos/clientes     ║"
echo "║  Pressione Ctrl+C para encerrar                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

sleep 1 && xdg-open "http://localhost:5050" >/dev/null 2>&1 &

python3 "$SCRIPT_DIR/pop_monitor_api.py"
