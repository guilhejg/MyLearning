#!/usr/bin/env python3
"""fan-modo: troca o modo da ventoinha do ThinkPad (thinkfan).

Uso:
  fan-modo              mostra o modo atual, temperatura e ventoinha
  fan-modo sala         silencioso: ventoinha parada até ficar obrigatório ligar
  fan-modo normal       teto no nível 4, emergência nível 7 a 85°C
  fan-modo max          todos os níveis, ventoinha acompanha a temperatura
  fan-modo -w           mostra temperatura/ventoinha ao vivo (Ctrl+C sai)
"""
import glob
import os
import re
import subprocess
import sys
import time

CONF = "/etc/thinkfan.conf"
MARK = "# fan-modo:"

# cada nível: [nível da ventoinha, sobe a partir de °C, desce abaixo de °C]
PERFIS = {
    "sala": ("silencioso: parada até 75°C; só liga se esquentar de verdade", [
        (0, 0, 75), (1, 70, 80), (2, 76, 85), (7, 82, 32767)]),
    "normal": ("teto no nível 4; nível 7 só a partir de 85°C", [
        (0, 0, 50), (1, 48, 60), (2, 58, 66), (3, 64, 72), (4, 68, 88), (7, 85, 32767)]),
    "max": ("todos os níveis (mais barulho, mais frio)", [
        (0, 0, 50), (1, 48, 58), (2, 56, 64), (3, 62, 68), (4, 66, 72),
        (5, 70, 76), (6, 74, 80), (7, 78, 32767)]),
}

USE_COLOR = sys.stdout.isatty()


def cor(t, c):
    return f"\033[{c}m{t}\033[0m" if USE_COLOR else t


def temps():
    try:
        out = subprocess.run(["sensors"], capture_output=True, text=True).stdout
        vals = [float(m) for m in re.findall(r"Core \d+:\s+\+([\d.]+)", out)]
        return vals
    except OSError:
        return []


def fan():
    d = {}
    try:
        for linha in open("/proc/acpi/ibm/fan"):
            k, _, v = linha.partition(":")
            d[k.strip()] = v.strip()
    except OSError:
        pass
    return d.get("level", "?"), d.get("speed", "?")


def modo_atual():
    try:
        for linha in open(CONF):
            if linha.startswith(MARK):
                return linha[len(MARK):].strip()
    except OSError:
        pass
    return "desconhecido (configuração manual)"


def status():
    t = temps()
    nivel, rpm = fan()
    ativo = subprocess.run(["systemctl", "is-active", "thinkfan"], capture_output=True, text=True).stdout.strip()
    print(f"Modo:       {cor(modo_atual(), 1)}")
    print(f"thinkfan:   {cor(ativo, 32) if ativo == 'active' else cor(ativo, 31)}")
    print(f"Ventoinha:  nível {nivel} ({rpm} RPM)")
    if t:
        pico = max(t)
        c = 32 if pico < 65 else 33 if pico < 80 else 31
        print(f"Núcleos:    {' / '.join(f'{x:.0f}°C' for x in t)}  " + cor("(máx %.0f°C)" % pico, c))


def aplicar(nome):
    desc, niveis = PERFIS[nome]
    if not os.path.exists(CONF):
        sys.exit(f"{CONF} não existe (thinkfan instalado?).")
    atual = open(CONF).read()
    cabeca = atual[:atual.index("levels:")] if "levels:" in atual else ""
    cabeca = "\n".join(l for l in cabeca.splitlines() if not l.startswith(MARK)).rstrip() + "\n"
    corpo = f"{MARK} {nome} - {desc}\nlevels:\n" + "".join(
        f"  - [{n}, {a}, {b}]\n" for n, a, b in niveis)
    if not os.path.exists(CONF + ".bak-fan-modo"):
        subprocess.run(["sudo", "cp", CONF, CONF + ".bak-fan-modo"], check=True)
    novo = cabeca + corpo
    tmp = f"/tmp/thinkfan.{os.getpid()}"
    open(tmp, "w").write(novo)
    subprocess.run(["sudo", "cp", tmp, CONF], check=True)
    os.remove(tmp)
    subprocess.run(["sudo", "systemctl", "restart", "thinkfan"], check=True)
    print(f"Modo '{nome}' ativado: {desc}")
    time.sleep(3)
    status()
    if nome == "sala":
        print(cor("\nAviso: em carga alta a ventoinha só liga a partir de ~70-75°C.", 33))


def ao_vivo():
    try:
        while True:
            t = temps()
            nivel, rpm = fan()
            pico = max(t) if t else 0
            c = 32 if pico < 65 else 33 if pico < 80 else 31
            print(f"\r{time.strftime('%H:%M:%S')}  núcleos {pico:.0f}°C  ventoinha nível {nivel} ({rpm} RPM)  [{modo_atual().split(' - ')[0]}]   ", end="", flush=True)
            time.sleep(2)
    except KeyboardInterrupt:
        print()


def main():
    args = sys.argv[1:]
    if not args:
        status()
    elif args[0] in PERFIS:
        aplicar(args[0])
    elif args[0] in ("-w", "--watch"):
        ao_vivo()
    else:
        print(__doc__)
        sys.exit(0 if args[0] in ("-h", "--help") else 1)


if __name__ == "__main__":
    main()
