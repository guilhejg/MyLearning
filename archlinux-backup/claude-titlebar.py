#!/usr/bin/env python3
"""claude-titlebar: usa a barra de título do sistema (XFCE) no Claude Desktop.

  claude-titlebar on       ativa a moldura nativa (faz backup na primeira vez)
  claude-titlebar off      volta ao original a partir do backup
  claude-titlebar status   mostra o estado atual

Edita /usr/lib/claude-desktop/resources/app.asar (precisa de sudo). A edição troca
texto por texto do MESMO tamanho, então nenhum offset do .asar muda.
Atualizações do pacote desfazem a edição: rode 'claude-titlebar on' de novo depois.
Reinicie o Claude Desktop para valer.
"""
import hashlib
import os
import subprocess
import sys

ASAR = "/usr/lib/claude-desktop/resources/app.asar"
BKP_DIR = os.path.expanduser("~/.local/share/claude-desktop-backup")
ORIG = os.path.join(BKP_DIR, "app.asar.orig")
# janela principal: esconde a moldura e desenha botões próprios -> moldura nativa
VELHO = b'titleBarStyle:"hidden",titleBarOverlay:!0,trafficLightPosition:'
NOVO = b'titleBarStyle:"default",titleBarOverlay:0,trafficLightPosition:'
assert len(VELHO) == len(NOVO)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def estado(dados):
    if VELHO in dados:
        return "original"
    if NOVO in dados:
        return "nativo"
    return "desconhecido"


def sudo_cp(src, dst):
    subprocess.run(["sudo", "cp", src, dst], check=True)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    dados = open(ASAR, "rb").read()
    est = estado(dados)
    if cmd == "status":
        print(f"Barra de título: {est}")
        print(f"Backup: {'existe' if os.path.exists(ORIG) else 'NÃO existe'} ({ORIG})")
        return
    if cmd == "on":
        if est == "nativo":
            return print("Já está com a barra de título nativa.")
        if est != "original" or dados.count(VELHO) != 1:
            sys.exit(f"Trecho não encontrado exatamente uma vez ({dados.count(VELHO)}). "
                     "O app foi atualizado; não vou editar às cegas.")
        os.makedirs(BKP_DIR, exist_ok=True)
        if not os.path.exists(ORIG):
            open(ORIG, "wb").write(dados)
            open(ORIG + ".sha256", "w").write(f"{sha(ORIG)}  app.asar.orig\n")
            print("Backup criado.")
        novo = dados.replace(VELHO, NOVO)
        assert len(novo) == len(dados)
        tmp = os.path.join(BKP_DIR, "app.asar.nativo")
        open(tmp, "wb").write(novo)
        sudo_cp(tmp, ASAR)
        print("Ativado. Feche e abra o Claude Desktop para valer.")
    elif cmd == "off":
        if not os.path.exists(ORIG):
            sys.exit("Sem backup para restaurar.")
        sudo_cp(ORIG, ASAR)
        print("Restaurado o original. Feche e abra o Claude Desktop.")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
