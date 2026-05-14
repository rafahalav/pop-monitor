"""
PoP Monitor — Server Performance API
====================================
Requisitos:
    pip install flask flask-cors psutil

Uso:
    python3 pop_monitor_api.py

Acesso local:    http://localhost:5050
Acesso na rede:  http://<IP-do-servidor>:5050
"""

import time
import threading
import datetime
import subprocess
import re
import collections
import platform
import socket
import os
import psutil
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR)
CORS(app)

# ── Configurações ─────────────────────────────────────────────────
PING_HOST     = "8.8.8.8"
PING_COUNT    = 10
COLLECT_EVERY = 4
MAX_HISTORY   = 60

# ── Estado compartilhado ──────────────────────────────────────────
history = {
    "cpu":     collections.deque(maxlen=MAX_HISTORY),
    "ram":     collections.deque(maxlen=MAX_HISTORY),
    "net_in":  collections.deque(maxlen=MAX_HISTORY),
    "net_out": collections.deque(maxlen=MAX_HISTORY),
    "latency": collections.deque(maxlen=MAX_HISTORY),
    "jitter":  collections.deque(maxlen=MAX_HISTORY),
}

_lock      = threading.Lock()
_prev_net  = psutil.net_io_counters()
_prev_time = time.time()


def _ping_stats(host, count):
    try:
        cmd = (["ping", "-n", str(count), host]
               if platform.system() == "Windows"
               else ["ping", "-c", str(count), "-i", "0.2", host])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        rtts = [float(x) for x in re.findall(r"time[=<](\d+\.?\d*)", result.stdout)]
        if not rtts:
            return None, None
        avg    = sum(rtts) / len(rtts)
        jitter = (sum(abs(rtts[i] - rtts[i-1]) for i in range(1, len(rtts))) / (len(rtts)-1)
                  if len(rtts) > 1 else 0.0)
        return round(avg, 2), round(jitter, 2)
    except Exception:
        return None, None


def _collect_loop():
    global _prev_net, _prev_time
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        net = psutil.net_io_counters()
        now = time.time()
        dt  = max(now - _prev_time, 0.001)
        in_g  = max((net.bytes_recv - _prev_net.bytes_recv) / dt / 1e9, 0)
        out_g = max((net.bytes_sent - _prev_net.bytes_sent) / dt / 1e9, 0)
        _prev_net  = net
        _prev_time = now
        lat, jit = _ping_stats(PING_HOST, PING_COUNT)
        with _lock:
            history["cpu"].append(round(cpu, 1))
            history["ram"].append(round(ram.percent, 1))
            history["net_in"].append(round(in_g, 5))
            history["net_out"].append(round(out_g, 5))
            if lat is not None:
                history["latency"].append(lat)
                history["jitter"].append(jit)
        time.sleep(max(COLLECT_EVERY - (time.time() - now), 0.5))


threading.Thread(target=_collect_loop, daemon=True, name="collector").start()


def _top_processes(n=5):
    procs = []
    for p in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
        try:
            if p.info["cpu_percent"] is not None:
                procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
    return [{"nome": (p["name"] or "?")[:22],
             "cpu":  round(p["cpu_percent"] or 0, 1),
             "ram":  round(p["memory_percent"] or 0, 1)} for p in procs[:n]]


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/metrics")
def metrics():
    cpu  = psutil.cpu_percent(interval=0.1)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net  = psutil.net_io_counters()
    freq = psutil.cpu_freq()
    uptime_h = round((time.time() - psutil.boot_time()) / 3600, 1)
    with _lock:
        h_cpu = list(history["cpu"]);  h_ram = list(history["ram"])
        h_ni  = list(history["net_in"]); h_no = list(history["net_out"])
        h_lat = list(history["latency"]); h_jit = list(history["jitter"])
    return jsonify({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "cpu": {"uso_pct": round(cpu,1), "nucleos": psutil.cpu_count(logical=True),
                "nucleos_fis": psutil.cpu_count(logical=False),
                "frequencia": round(freq.current) if freq else None,
                "freq_max":   round(freq.max)      if freq else None},
        "ram": {"uso_pct": round(ram.percent,1), "total_gb": round(ram.total/1e9,1),
                "usado_gb": round(ram.used/1e9,1), "livre_gb": round(ram.available/1e9,1)},
        "disco": {"uso_pct": round(disk.percent,1), "total_gb": round(disk.total/1e9,1),
                  "usado_gb": round(disk.used/1e9,1), "livre_gb": round(disk.free/1e9,1)},
        "uptime_horas": uptime_h,
        "rede": {"entrada_gbps": round(h_ni[-1] if h_ni else 0,5),
                 "saida_gbps":   round(h_no[-1] if h_no else 0,5),
                 "pacotes_in": net.packets_recv, "pacotes_out": net.packets_sent,
                 "erros_in": net.errin, "erros_out": net.errout,
                 "perda_pct": 0, "host_ping": PING_HOST},
        "latencia": {"atual_ms": h_lat[-1] if h_lat else None,
                     "media_ms": round(sum(h_lat)/len(h_lat),2) if h_lat else None,
                     "min_ms": min(h_lat) if h_lat else None,
                     "max_ms": max(h_lat) if h_lat else None,
                     "amostras": len(h_lat)},
        "jitter":  {"atual_ms": h_jit[-1] if h_jit else None,
                    "media_ms": round(sum(h_jit)/len(h_jit),2) if h_jit else None,
                    "max_ms":   max(h_jit) if h_jit else None,
                    "amostras": len(h_jit)},
        "historico": {"cpu": h_cpu, "ram": h_ram,
                      "net_in": h_ni, "net_out": h_no,
                      "latency": h_lat, "jitter": h_jit},
        "processos_top": _top_processes(5),
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok", "ts": datetime.datetime.now().isoformat()})


if __name__ == "__main__":
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    print("\n" + "=" * 55)
    print("  PoP Monitor — Dashboard de Performance")
    print("=" * 55)
    print(f"  Local   →  http://localhost:5050")
    print(f"  Rede    →  http://{local_ip}:5050")
    print(f"  Ping    →  {PING_HOST}  |  count: {PING_COUNT}")
    print("=" * 55)
    print("  Compartilhe o link 'Rede' com técnicos/clientes")
    print("  Ctrl+C para encerrar\n")

    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)
