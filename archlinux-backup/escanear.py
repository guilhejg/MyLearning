#!/usr/bin/env python3
"""escanear: escaneia pelo scanner de rede (eSCL/AirScan), sem depender do SANE.

  escanear                    JPEG colorido, 200 dpi, em ~/Documentos/Escaneados
  escanear -f pdf             salva em PDF
  escanear -r 300 -c cinza    300 dpi em tons de cinza  (cores: cor | cinza | pb)
  escanear -o ~/Desktop       outra pasta
  escanear -i 192.168.0.50    endereço do scanner (por padrão procura sozinho)
  escanear -n 3               escaneia 3 folhas, uma de cada vez (troca no vidro)
"""
import argparse
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

COR = {"cor": "RGB24", "cinza": "Grayscale8", "pb": "BlackAndWhite1"}
FORMATO = {"jpg": "image/jpeg", "pdf": "application/pdf"}


def achar_scanner():
    """Procura um scanner eSCL na rede por mDNS (avahi). Devolve (ip, porta, caminho)."""
    try:
        out = subprocess.run(["avahi-browse", "-rtp", "_uscan._tcp"], capture_output=True,
                             text=True, timeout=12).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    for linha in out.splitlines():
        c = linha.split(";")
        if linha.startswith("=") and len(c) >= 10 and c[2] == "IPv4":
            rs = re.search(r"\"rs=([^\"]*)\"", c[9])
            return c[7], c[8], "/" + (rs.group(1) if rs else "eSCL").strip("/")
    return None


def xml_trabalho(dpi, cor, fmt):
    # A4 em 1/300 de polegada
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<scan:ScanSettings xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03" xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm">
  <pwg:Version>2.1</pwg:Version>
  <scan:Intent>Document</scan:Intent>
  <pwg:ScanRegions><pwg:ScanRegion>
    <pwg:ContentRegionUnits>escl:ThreeHundredthsOfInches</pwg:ContentRegionUnits>
    <pwg:XOffset>0</pwg:XOffset><pwg:YOffset>0</pwg:YOffset>
    <pwg:Width>2480</pwg:Width><pwg:Height>3508</pwg:Height>
  </pwg:ScanRegion></pwg:ScanRegions>
  <pwg:InputSource>Platen</pwg:InputSource>
  <scan:ColorMode>{COR[cor]}</scan:ColorMode>
  <scan:XResolution>{dpi}</scan:XResolution><scan:YResolution>{dpi}</scan:YResolution>
  <pwg:DocumentFormat>{FORMATO[fmt]}</pwg:DocumentFormat>
</scan:ScanSettings>""".encode()


def escanear_uma(base, dpi, cor, fmt, destino):
    req = urllib.request.Request(f"{base}/ScanJobs", data=xml_trabalho(dpi, cor, fmt),
                                 headers={"Content-Type": "text/xml"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            loc = r.headers.get("Location")
    except urllib.error.HTTPError as e:
        sys.exit(f"O scanner recusou o trabalho (HTTP {e.code}). Ocupado ou tampa aberta?")
    if not loc:
        sys.exit("O scanner não devolveu o endereço do trabalho.")
    loc = loc if loc.startswith("http") else f"{base.split('/eSCL')[0]}{loc}"
    for _ in range(3):
        try:
            with urllib.request.urlopen(f"{loc}/NextDocument", timeout=120) as r:
                dados = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code in (409, 503):
                time.sleep(2)
                continue
            sys.exit(f"Falha ao baixar o documento (HTTP {e.code}).")
    else:
        sys.exit("O scanner não terminou a tempo.")
    open(destino, "wb").write(dados)
    return len(dados)


def main():
    ap = argparse.ArgumentParser(description="Escaneia pelo scanner de rede", add_help=True)
    ap.add_argument("-r", "--resolucao", type=int, default=200, choices=[75, 100, 150, 200, 300, 600])
    ap.add_argument("-c", "--cor", default="cor", choices=list(COR))
    ap.add_argument("-f", "--formato", default="jpg", choices=list(FORMATO))
    ap.add_argument("-o", "--saida", default="~/Documentos/Escaneados")
    ap.add_argument("-i", "--ip", help="endereço do scanner (padrão: procurar por mDNS)")
    ap.add_argument("-n", "--folhas", type=int, default=1)
    a = ap.parse_args()

    if a.ip:
        base = f"http://{a.ip}:8080/eSCL"
    else:
        achado = achar_scanner()
        if not achado:
            sys.exit("Nenhum scanner encontrado na rede. Use -i ENDEREÇO.")
        base = f"http://{achado[0]}:{achado[1]}{achado[2]}"
    pasta = os.path.expanduser(a.saida)
    os.makedirs(pasta, exist_ok=True)
    print(f"Scanner: {base}")
    for n in range(1, a.folhas + 1):
        if a.folhas > 1 and n > 1:
            input(f"Coloque a folha {n} no vidro e aperte Enter... ")
        nome = f"escaneado-{datetime.now():%Y%m%d-%H%M%S}" + (f"-{n}" if a.folhas > 1 else "")
        destino = os.path.join(pasta, f"{nome}.{a.formato}")
        print(f"Escaneando folha {n}/{a.folhas} ({a.resolucao} dpi, {a.cor})...")
        tam = escanear_uma(base, a.resolucao, a.cor, a.formato, destino)
        print(f"  salvo: {destino} ({tam / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
