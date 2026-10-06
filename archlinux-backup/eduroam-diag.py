#!/usr/bin/env python3
"""eduroam-diag: diagnostica problemas de conexão com a eduroam (NetworkManager + wpa_supplicant).

Uso: ./eduroam-diag.py [-m MINUTOS] [-s SSID] [--sem-scan]
"""
import argparse
import re
import shutil
import socket
import subprocess
import sys
from collections import Counter

USE_COLOR = sys.stdout.isatty()


def c(txt, code):
    return f"\033[{code}m{txt}\033[0m" if USE_COLOR else txt


OK, WARN, BAD, INFO = (lambda t: c(t, 32)), (lambda t: c(t, 33)), (lambda t: c(t, 31)), (lambda t: c(t, 36))
BOLD = lambda t: c(t, 1)

findings = []  # (severidade 0=ok 1=aviso 2=problema, mensagem)


def add(sev, msg):
    findings.append((sev, msg))


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, "", str(e)


def title(t):
    print(f"\n{BOLD('== ' + t + ' ==')}")


def split_terse(line):
    """Divide linha do `nmcli -t` respeitando ':' escapado (\\:)."""
    return [p.replace("\\:", ":") for p in re.split(r"(?<!\\):", line)]


# ---------------------------------------------------------------- interface
def wifi_device():
    _, out, _ = run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device"])
    for line in out.splitlines():
        dev, typ, state, conn = (split_terse(line) + ["", "", "", ""])[:4]
        if typ == "wifi":
            return dev, state, conn
    return None, None, None


def check_interface():
    title("Placa Wi-Fi")
    dev, state, conn = wifi_device()
    if not dev:
        add(2, "Nenhuma placa Wi-Fi encontrada pelo NetworkManager.")
        print(BAD("Nenhuma placa Wi-Fi encontrada."))
        return None, None
    _, out, _ = run(["nmcli", "radio", "wifi"])
    if out.strip() != "enabled":
        add(2, "O Wi-Fi está DESLIGADO (rádio desativado). Ative com: nmcli radio wifi on")
        print(BAD("Rádio Wi-Fi desligado."))
    rc, out, _ = run(["rfkill", "list", "wifi"])
    if "Hard blocked: yes" in out:
        add(2, "Wi-Fi bloqueado por botão/chave física do notebook (hard block).")
    elif "Soft blocked: yes" in out:
        add(2, "Wi-Fi bloqueado por software (rfkill). Use: rfkill unblock wifi")
    print(f"Dispositivo: {dev}   Estado: {state}   Conexão: {conn or '-'}")
    return dev, conn


# ------------------------------------------------------------ sinal atual
def dbm_label(dbm):
    if dbm >= -55:
        return OK("excelente"), 0
    if dbm >= -67:
        return OK("bom"), 0
    if dbm >= -75:
        return WARN("fraco"), 1
    return BAD("muito fraco"), 2


def check_current_link(dev):
    if not dev or not shutil.which("iw"):
        return
    rc, out, _ = run(["iw", "dev", dev, "link"])
    if "Not connected" in out or rc != 0:
        return
    ssid = re.search(r"SSID: (.*)", out)
    sig = re.search(r"signal: (-?\d+) dBm", out)
    rate = re.search(r"tx bitrate: ([\d.]+) MBit/s", out)
    title("Link atual")
    name = ssid.group(1) if ssid else "?"
    name = re.sub(r"(?:\\x[0-9a-fA-F]{2})+", lambda m: bytes.fromhex(m.group().replace("\\x", "")).decode("utf-8", "replace"), name)
    print(f"Rede: {name}")
    if sig:
        dbm = int(sig.group(1))
        lbl, sev = dbm_label(dbm)
        print(f"Sinal: {dbm} dBm ({lbl})" + (f"   Taxa: {rate.group(1)} Mbit/s" if rate else ""))
        if sev:
            add(sev, f"Sinal da rede atual está fraco ({dbm} dBm): aproxime-se do roteador/AP.")


# ----------------------------------------------------------------- scan
def check_scan(ssid, rescan):
    title(f"Redes '{ssid}' no ar")
    cmd = ["nmcli", "-t", "-f", "IN-USE,SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY", "dev", "wifi", "list"]
    if rescan:
        cmd += ["--rescan", "yes"]
    rc, out, err = run(cmd, timeout=30)
    if rc != 0:
        print(WARN(f"Não consegui escanear: {err.strip() or 'erro desconhecido'}"))
        return
    aps = []
    for line in out.splitlines():
        f = split_terse(line)
        if len(f) >= 7 and f[1] == ssid:
            aps.append(dict(use=f[0] == "*", bssid=f[2], chan=f[3], freq=f[4], sig=int(f[5] or 0), sec=f[6]))
    if not aps:
        print(BAD(f"Nenhum AP '{ssid}' encontrado."))
        add(2, f"A '{ssid}' NÃO aparece no scan: você está fora da cobertura (longe demais) ou "
               "o AP está fora do ar. Tente se aproximar de um ponto de acesso.")
        return
    aps.sort(key=lambda a: -a["sig"])
    for a in aps:
        mark = "*" if a["use"] else " "
        bar = "█" * (a["sig"] // 10)
        col = OK if a["sig"] >= 60 else WARN if a["sig"] >= 35 else BAD
        print(f" {mark} {a['bssid']}  canal {a['chan']:>3} ({a['freq']})  {col(f'{a['sig']:>3}% {bar}')}")
    best = aps[0]["sig"]
    print(f"{len(aps)} AP(s) visível(is); melhor sinal: {best}%")
    if best < 25:
        add(2, f"Sinal da {ssid} MUITO fraco ({best}%): você está longe demais do AP mais próximo.")
    elif best < 40:
        add(1, f"Sinal da {ssid} fraco ({best}%): conexão tende a cair ou falhar na autenticação.")
    else:
        add(0, f"Sinal da {ssid} é suficiente ({best}%): distância provavelmente não é o problema.")
    if all(a["sec"] == "" or "802.1X" not in a["sec"] for a in aps):
        add(1, f"Os APs '{ssid}' visíveis não anunciam WPA2-Enterprise (802.1X): pode ser um AP falso/mal configurado.")


# --------------------------------------------------------- perfil do NM
def check_profile(ssid):
    title(f"Perfil salvo da '{ssid}'")
    _, out, _ = run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"])
    names = [split_terse(l)[0] for l in out.splitlines() if "wireless" in l]
    prof = None
    for n in names:
        _, o, _ = run(["nmcli", "-t", "-f", "802-11-wireless.ssid", "connection", "show", n])
        if o.strip().endswith(ssid):
            prof = n
            break
    if not prof:
        print(WARN(f"Nenhum perfil salvo para '{ssid}'."))
        add(1, f"Não há perfil salvo para a {ssid} (nunca configurada neste notebook?).")
        return
    _, o, _ = run(["nmcli", "-t", "-s", "-f", "802-1x.eap,802-1x.identity,802-1x.anonymous-identity,"
                   "802-1x.ca-cert,802-1x.domain-suffix-match,802-1x.phase2-auth,802-1x.password-flags",
                   "connection", "show", prof])
    d = {}
    for line in o.splitlines():
        k, _, v = line.partition(":")
        d[k] = v.strip()
    print(f"Perfil: {prof}")
    print(f"  EAP: {d.get('802-1x.eap') or '-'}   Fase 2: {d.get('802-1x.phase2-auth') or '-'}")
    ident = d.get("802-1x.identity", "")
    print(f"  Identidade: {ident or '-'}   Anônima: {d.get('802-1x.anonymous-identity') or '-'}")
    if not ident:
        add(2, "O perfil da eduroam não tem identidade (usuário) configurada.")
    elif "@" not in ident:
        add(2, f"Identidade '{ident}' sem domínio: na eduroam o usuário deve ser completo "
               "(ex.: seu.login@ufmt.br).")
    elif not ident.lower().endswith("ufmt.br"):
        add(1, f"Identidade '{ident}' não termina em ufmt.br; confirme com o CPD/STI da UFMT.")
    if not d.get("802-1x.ca-cert"):
        add(1, "Perfil sem certificado CA: aceita qualquer servidor (inseguro) e pode falhar se a rede exigir validação.")
    if d.get("802-1x.password-flags") == "1":
        print("  Senha: pedida a cada conexão (não salva)")


# ------------------------------------------------------------------- logs
# (regex, chave, severidade, diagnóstico)
PATTERNS = [
    (r"EAP-MSCHAPV2: Authentication failed|MSCHAPV2: .*failed|Wrong password|password.*(expired|incorrect)",
     "senha", 2, "SENHA/USUÁRIO recusado pelo servidor da UFMT (senha errada, expirada ou conta bloqueada). "
                 "Teste o login no portal/e-mail institucional e redefina a senha se necessário."),
    (r"no-secrets|Secrets were required, but not provided",
     "senha_ausente", 2, "O NetworkManager não tem a SENHA salva/disponível (keyring bloqueado ou senha não armazenada)."),
    (r"CTRL-EVENT-EAP-TLS-CERT-ERROR|TLS: Certificate verification failed|certificate (has )?expired|"
     r"certificate is not yet valid|SSL: .*certificate",
     "cert", 2, "Problema de CERTIFICADO do servidor RADIUS (expirado, CA diferente ou domínio não confere). "
                 "Se a UFMT trocou o certificado, atualize o CA/domain do perfil. Verifique também o relógio do PC."),
    (r"EAP-TLS|TLS: tls_connection_handshake failed|SSL_connect:error|handshake failed",
     "tls", 1, "Falha no handshake TLS com o servidor de autenticação (RADIUS) — possível problema do lado da UFMT."),
    (r"CTRL-EVENT-EAP-FAILURE|EAP authentication failed",
     "eap", 2, "Autenticação 802.1X (EAP) FALHOU: credenciais recusadas OU servidor RADIUS com erro."),
    (r"EAP: .*(timeout|timed out)|CTRL-EVENT-EAP-TIMEOUT|No EAP response|EAP-.*retransmit",
     "radius", 2, "Servidor de autenticação (RADIUS) NÃO RESPONDEU: erro interno/instabilidade na infraestrutura da UFMT."),
    (r"Authentication with [0-9a-f:]{17} timed out|auth.*timed out|Authentication request .* timed out",
     "auth_timeout", 1, "AP não respondeu à autenticação: sinal fraco/AP sobrecarregado ou muito distante."),
    (r"Association request to the driver failed|ASSOC-REJECT|association.*timed out|"
     r"Association with [0-9a-f:]{17} timed out",
     "assoc", 1, "O AP rejeitou/ignorou a associação (AP lotado, sinal fraco ou problema no AP)."),
    (r"4-Way Handshake failed|WPA: .*handshake.*(timeout|failed)|reason=15",
     "handshake", 2, "Handshake de chaves (4-way) falhou: sinal ruim/interferência ou AP com defeito."),
    (r"CTRL-EVENT-SSID-TEMP-DISABLED",
     "tempdis", 1, "O wpa_supplicant desativou temporariamente a rede após falhas repetidas (aguarde ~10s ou reconecte)."),
    (r"dhcp4 \(.*(request timed out|failed)|ip-config-unavailable|dhcp-start-failed",
     "dhcp", 2, "Autenticou, mas NÃO recebeu endereço IP (DHCP): servidor DHCP/VLAN da rede com problema (lado da UFMT)."),
    (r"supplicant-timeout|supplicant-failed",
     "supp", 1, "wpa_supplicant demorou/falhou ao responder (sinal fraco, rede instável ou erro interno do cliente)."),
]

REASONS = {
    1: "motivo não especificado", 2: "autenticação anterior inválida", 3: "AP desconectou/expulsou você",
    4: "inatividade", 5: "AP sobrecarregado (muitos clientes)", 6: "frame inválido (classe 2)",
    7: "frame inválido (classe 3)", 8: "você saiu do AP (roaming)", 15: "timeout do handshake de 4 vias",
    16: "timeout da chave de grupo", 23: "falha de autenticação 802.1X", 34: "condições ruins do canal (sinal fraco)",
}


def check_logs(minutes, ssid):
    title(f"Logs (últimos {minutes} min)")
    rc, out, err = run(["journalctl", "-u", "NetworkManager", "-u", "wpa_supplicant", "--since",
                        f"{minutes} min ago", "--no-pager", "-o", "short"], timeout=30)
    if rc != 0 or not out.strip():
        msg = err.strip() or "sem registros no período"
        print(WARN(f"Não consegui ler logs: {msg}"))
        if "not seeing messages" in err.lower() or "permission" in err.lower():
            print("Dica: adicione seu usuário ao grupo 'systemd-journal' (ou rode com sudo).")
        return
    lines = out.splitlines()
    counts, last = Counter(), {}
    reasons = Counter()
    for line in lines:
        for rx, key, sev, _ in PATTERNS:
            if re.search(rx, line, re.I):
                counts[key] += 1
                last[key] = line
        m = re.search(r"CTRL-EVENT-DISCONNECT.*reason=(\d+)(?: locally_generated=(\d))?", line)
        if m:
            reasons[(int(m.group(1)), m.group(2) == "1")] += 1
    # tentativas de ativação de eduroam
    n_act = sum(1 for l in lines if re.search(r"Activation:.*starting connection", l) and ssid.lower() in l.lower())
    n_ok = sum(1 for l in lines if re.search(r"Activation:.*successful", l) and ssid.lower() in l.lower())
    if n_act or n_ok:
        print(f"Tentativas de conectar na {ssid}: {n_act}   Sucessos: {n_ok}")
    if not counts and not reasons:
        print(OK("Nenhum erro conhecido nos logs do período."))
        return
    for rx, key, sev, diag in PATTERNS:
        if counts[key]:
            col = BAD if sev == 2 else WARN
            print(f"{col('•')} {counts[key]}x  {diag}")
            print(f"    último: {last[key][:150]}")
            add(sev, diag + f" ({counts[key]}x nos logs)")
    for (code, local), n in reasons.most_common(5):
        who = "iniciado pelo seu PC" if local else "iniciado pelo AP/rede"
        print(f"{INFO('•')} {n}x desconexão código {code}: {REASONS.get(code, 'outro')} ({who})")
        if code in (3, 4, 5, 34) and not local:
            add(1, f"AP derrubou a conexão {n}x: {REASONS[code]}.")
        if code == 15 or code == 34:
            add(2, f"Desconexões por {REASONS[code]} ({n}x): problema de sinal/interferência.")


# ---------------------------------------------------------- relógio (TLS)
def check_clock():
    rc, out, _ = run(["timedatectl", "show", "-p", "NTPSynchronized", "--value"])
    if out.strip() == "no":
        add(1, "Relógio do sistema NÃO sincronizado: pode causar erro de certificado na eduroam "
               "(sudo timedatectl set-ntp true).")


# --------------------------------------------------------- conectividade
def check_connectivity(dev, conn):
    if not conn:
        return
    title("Conectividade (rede atual)")
    rc, out, _ = run(["ip", "route", "show", "default", "dev", dev])
    gw = re.search(r"via (\S+)", out)
    tests = []
    if gw:
        tests.append(("Gateway", gw.group(1)))
    else:
        add(2, "Conectado mas SEM rota padrão/gateway (DHCP incompleto).")
        print(BAD("Sem gateway padrão."))
    tests.append(("Internet (1.1.1.1)", "1.1.1.1"))
    for name, host in tests:
        rc, out, _ = run(["ping", "-c", "4", "-W", "2", "-q", host], timeout=20)
        loss = re.search(r"([\d.]+)% packet loss", out)
        rtt = re.search(r"= [\d.]+/([\d.]+)/", out)
        l = float(loss.group(1)) if loss else 100.0
        txt = f"{l:.0f}% perda" + (f", {rtt.group(1)} ms" if rtt else "")
        print(f"{name:<20} {(OK if l == 0 else WARN if l < 100 else BAD)(txt)}")
        if name.startswith("Gateway") and l >= 50:
            add(2, f"Gateway com {l:.0f}% de perda: link Wi-Fi instável (sinal) ou AP com problema.")
        elif name.startswith("Internet") and l >= 50:
            add(2 if gw and not any("Gateway com" in m for _, m in findings) else 1,
                f"Sem acesso à internet ({l:.0f}% de perda) apesar de estar conectado.")
    try:
        socket.setdefaulttimeout(4)
        socket.gethostbyname("google.com")
        print(f"{'DNS':<20} {OK('ok')}")
    except OSError:
        print(f"{'DNS':<20} {BAD('falhou')}")
        add(2, "DNS não resolve nomes: servidor DNS da rede fora do ar (tente 1.1.1.1/8.8.8.8).")


# ---------------------------------------------------------------- veredito
def verdict():
    title("DIAGNÓSTICO")
    probs = [m for s, m in findings if s == 2]
    warns = [m for s, m in findings if s == 1]
    oks = [m for s, m in findings if s == 0]
    for m in probs:
        print(f"{BAD('✘')} {m}")
    for m in warns:
        print(f"{WARN('!')} {m}")
    for m in oks:
        print(f"{OK('✔')} {m}")
    if not probs and not warns:
        print(OK("Nada de errado detectado agora. Se o problema é intermitente, rode de novo logo após uma falha."))
    elif probs:
        print(f"\n{BOLD('Mais provável:')} {probs[0]}")


def main():
    ap = argparse.ArgumentParser(description="Diagnóstico da eduroam")
    ap.add_argument("-m", "--minutos", type=int, default=60, help="janela de logs (padrão: 60)")
    ap.add_argument("-s", "--ssid", default="eduroam")
    ap.add_argument("--sem-scan", action="store_true", help="não força novo scan")
    a = ap.parse_args()
    if not shutil.which("nmcli"):
        sys.exit("nmcli (NetworkManager) não encontrado.")
    print(BOLD(f"eduroam-diag — verificando '{a.ssid}'..."))
    dev, conn = check_interface()
    check_current_link(dev)
    check_scan(a.ssid, not a.sem_scan)
    check_profile(a.ssid)
    check_clock()
    check_logs(a.minutos, a.ssid)
    check_connectivity(dev, conn)
    verdict()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
