# PoP Monitor

**Real-time network observability dashboard for FTTH and ISP environments.**

![License](https://img.shields.io/github/license/rafahalav/pop-monitor)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

PoP Monitor é um dashboard de performance em tempo real desenvolvido para ISPs, provedores FTTH e equipes de NOC. Monitora CPU, RAM, disco, tráfego de rede, latência e jitter diretamente do servidor, acessível por qualquer navegador na rede local ou pela internet.

---

## ✨ Funcionalidades

- **CPU, RAM e Disco** — uso em tempo real com histórico em gráfico
- **Tráfego de rede** — entrada e saída em Gbps
- **Latência (RTT)** — ping real com classificação de qualidade
- **Jitter** — variação entre pings consecutivos
- **Top processos** — os 5 processos que mais consomem CPU
- **Acesso em rede** — qualquer dispositivo na LAN acessa pelo navegador
- **Sem dependências no cliente** — só um navegador é necessário

---

## 🖥️ Requisitos

- Python 3.8 ou superior
- Linux, Windows ou macOS
- Conexão com a internet (para ping ao `8.8.8.8`)

---

## 🚀 Instalação

### 🐧 Linux / 🍎 macOS

```bash
# 1. Clone o repositório
git clone https://github.com/rafahalav/pop-monitor.git
cd pop-monitor

# 2. Crie o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie
python3 pop_monitor_api.py
```

Ou use o script de inicialização:

```bash
chmod +x iniciar.sh
./iniciar.sh
```

---

### 🪟 Windows

```bash
# 1. Clone o repositório
git clone https://github.com/rafahalav/pop-monitor.git
cd pop-monitor

# 2. Crie o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie
python pop_monitor_api.py
```

---

## 🌐 Acesso

Após iniciar, o terminal exibirá:

```
╔══════════════════════════════════════════════════════╗
║           PoP Monitor — em execução                  ║
╠══════════════════════════════════════════════════════╣
║  Local  →  http://localhost:5050                     ║
║  Rede   →  http://192.168.1.100:5050                 ║
╚══════════════════════════════════════════════════════╝
```

- **Local** — acesse na própria máquina
- **Rede** — compartilhe com técnicos e clientes na mesma rede LAN/Wi-Fi

---

## 🌍 Acesso pela internet (ngrok)

Para expor o dashboard fora da rede local:

```bash
# Instale o ngrok: https://ngrok.com/download
ngrok http 5050
```

O ngrok gerará um link público temporário. Compartilhe com quem precisar.

---

## ⚙️ Configuração

Edite as variáveis no início do `pop_monitor_api.py`:

| Variável | Padrão | Descrição |
|---|---|---|
| `PING_HOST` | `8.8.8.8` | Host usado para medir latência/jitter |
| `PING_COUNT` | `10` | Número de pings por rodada |
| `COLLECT_EVERY` | `4` | Intervalo de coleta em segundos |
| `MAX_HISTORY` | `60` | Amostras mantidas no histórico |

---

## 📁 Estrutura

```
pop-monitor/
├── pop_monitor_api.py   # Backend Flask — coleta e serve métricas
├── index.html           # Frontend — dashboard visual
├── requirements.txt     # Dependências Python
├── iniciar.sh           # Script de inicialização (Linux/macOS)
└── README.md
```

---

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças maiores, abra uma issue primeiro.

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

MIT © [rafahalav](https://github.com/rafahalav)
