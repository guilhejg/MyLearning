#!/usr/bin/env bash
# Reproduz as configurações feitas no ThinkPad (Arch Linux + XFCE + NetworkManager).
# Uso: ./setup.sh [módulo ...]     (sem argumentos, mostra a lista de módulos)
#      ./setup.sh all              (roda todos, exceto 'eduroam-senha')
# Cada módulo é idempotente: pode rodar de novo sem estragar nada.
# Rode como usuário comum; o script chama sudo quando precisa.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$HOME/.local/bin"
BG="$HOME/Documentos/Wallpapers"

say() { printf '\n==> %s\n' "$*"; }

# --------------------------------------------------------------- eduroam
mod_eduroam_diag() {
  say "Instalando eduroam-diag em $BIN"
  mkdir -p "$BIN"
  install -m 755 "$HERE/eduroam-diag.py" "$BIN/eduroam-diag"
  command -v fish >/dev/null && fish -c 'fish_add_path ~/.local/bin' || true
}

# Pede a senha sem mostrar na tela e grava no perfil 'eduroam' do NetworkManager.
# Causa do problema original: perfil sem senha salva => erro 'no-secrets'.
mod_eduroam_senha() {
  say "Gravando senha no perfil 'eduroam' (a senha não é salva neste repositório)"
  read -rsp "Senha da eduroam: " pw; echo
  nmcli connection modify eduroam 802-1x.password-flags 0 802-1x.password "$pw"
  unset pw
  echo "Pronto. Teste: nmcli connection up eduroam"
}

# ------------------------------------------------------------- minecraft
mod_minecraft() {
  say "Java 8 e 17 + xorg-xrandr"
  # xorg-xrandr: o LWJGL 2 do Minecraft 1.12.2 roda o comando 'xrandr';
  # sem ele o jogo cai com ArrayIndexOutOfBoundsException: 0 ao iniciar.
  sudo pacman -S --needed --noconfirm jre8-openjdk jre17-openjdk xorg-xrandr
  cat <<EOF

O TLauncher não está nos repositórios do Arch nem no AUR.
Baixe o .zip do site oficial (tlauncher.org) no navegador, coloque em ~/Downloads
e rode:  ./setup.sh tlauncher
EOF
}

mod_tlauncher() {
  local zip
  zip="$(ls -t "$HOME"/Downloads/TLauncher*.zip 2>/dev/null | head -1 || true)"
  [ -n "$zip" ] || { echo "Nenhum TLauncher*.zip em ~/Downloads."; return 1; }
  say "Instalando TLauncher a partir de $zip"
  local dir="$HOME/.local/share/tlauncher" java8=/usr/lib/jvm/java-8-openjdk/jre/bin/java
  mkdir -p "$dir" "$HOME/.local/share/applications"
  unzip -oq "$zip" -d "$dir"
  cat > "$HOME/.local/share/applications/tlauncher.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=TLauncher
Comment=Minecraft launcher
Exec=$java8 -jar $dir/TLauncher.jar
Path=$dir
Terminal=false
Categories=Game;
StartupWMClass=TLauncher
EOF
  update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
  echo "Dentro do launcher, escolha Release 1.12.2."
}

# ----------------------------------------------------------------- steam
mod_steam() {
  say "Steam via Flatpak (o repositório multilib não está ativado no pacman)"
  flatpak install -y flathub com.valvesoftware.Steam
  flatpak override --user --device=input com.valvesoftware.Steam   # controles/gamepads
  echo "Obs.: em redes que interceptam HTTPS (eduroam) a Steam não consegue se atualizar."
}

# ---------------------------------------------------------- energia / cpu
mod_energia() {
  say "TLP: governor schedutil, turbo ligado, EPP balanceado"
  local conf=/etc/tlp.d/01-economia.conf
  [ -f "$conf" ] || { echo "Sem $conf; pulando (instale tlp e crie o arquivo antes)."; return 0; }
  sudo cp -n "$conf" "$conf.bak-performance"
  sudo sed -i \
    -e 's/^CPU_SCALING_GOVERNOR_ON_AC=.*/CPU_SCALING_GOVERNOR_ON_AC=schedutil/' \
    -e 's/^CPU_SCALING_GOVERNOR_ON_BAT=.*/CPU_SCALING_GOVERNOR_ON_BAT=schedutil/' \
    -e 's/^CPU_ENERGY_PERF_POLICY_ON_AC=.*/CPU_ENERGY_PERF_POLICY_ON_AC=balance_performance/' \
    -e 's/^CPU_ENERGY_PERF_POLICY_ON_BAT=.*/CPU_ENERGY_PERF_POLICY_ON_BAT=balance_power/' "$conf"
  sudo tlp start || true
}

mod_boot() {
  say "Desativando NetworkManager-wait-online (boot mais rápido)"
  sudo systemctl disable NetworkManager-wait-online.service
}

mod_limpeza() {
  say "Limpeza de cache"
  sudo pacman -S --needed --noconfirm pacman-contrib
  sudo systemctl enable --now paccache.timer
  sudo paccache -rk1
  sudo paccache -ruk0
  rm -rf "$HOME/.cache/go-build" "$HOME"/.cache/google-chrome/*/Cache* 2>/dev/null || true
}

mod_xfce() {
  say "XFCE: compositor desligado e suspender ao fechar a tampa"
  xfconf-query -c xfwm4 -p /general/use_compositing -n -t bool -s false
  for k in lid-action-on-battery lid-action-on-ac; do
    xfconf-query -c xfce4-power-manager -p "/xfce4-power-manager/$k" -n -t uint -s 1
  done
}

# ---------------------------------------------------------------- idioma
mod_idioma() {
  say "Idioma do sistema: pt_BR.UTF-8 (faça logout/login depois)"
  sudo sed -i 's/^#\(pt_BR.UTF-8 UTF-8\)/\1/' /etc/locale.gen
  sudo locale-gen
  sudo localectl set-locale LANG=pt_BR.UTF-8
}

# -------------------------------------------------------------- ortografia
# Não existe interruptor global: cada app tem o seu. Aqui: Chrome e Claude Desktop
# (com o app FECHADO, senão ele sobrescreve o arquivo) e remoção do aspell.
mod_corretor_off() {
  say "Desativando corretor ortográfico"
  sudo pacman -Rns --noconfirm aspell-pt aspell 2>/dev/null || true
  python3 - <<'EOF'
import json, os, shutil, subprocess
for p, proc in (("~/.config/google-chrome/Default/Preferences", "/opt/google/chrome/chrome"),
                ("~/.config/Claude/Preferences", "/usr/lib/claude-desktop")):
    p = os.path.expanduser(p)
    if not os.path.exists(p):
        continue
    # com o app aberto ele sobrescreve o arquivo ao fechar
    if subprocess.run(["pgrep", "-f", proc], capture_output=True).returncode == 0:
        print("Feche o app e rode de novo para ajustar:", p)
        continue
    shutil.copy(p, p + ".bak-spell")
    d = json.load(open(p))
    d.setdefault("browser", {})["enable_spellchecking"] = False
    d.setdefault("spellcheck", {})["dictionaries"] = []
    d["spellcheck"]["dictionary"] = ""
    json.dump(d, open(p, "w"), separators=(",", ":"))
    print("ok:", p)
EOF
}

# ---------------------------------------------- Thunar: Espaço = Quick Look
mod_quicklook() {
  say "Sushi + atalho Espaço no Thunar"
  sudo pacman -S --needed --noconfirm sushi
  thunar -q 2>/dev/null || true; sleep 1
  mkdir -p "$HOME/.config/Thunar"
  python3 - <<'EOF'
import os
uid = "1790800000000000-1"
p = os.path.expanduser("~/.config/Thunar/uca.xml")
s = open(p).read() if os.path.exists(p) else '<?xml version="1.0" encoding="UTF-8"?>\n<actions>\n</actions>\n'
if uid not in s:
    act = f'''<action>
	<icon>document-properties</icon>
	<name>Pré-visualizar (Quick Look)</name>
	<submenu></submenu>
	<unique-id>{uid}</unique-id>
	<command>sushi %u</command>
	<description>Pré-visualiza o arquivo selecionado, como o Quick Look do macOS</description>
	<range>1</range>
	<patterns>*</patterns>
	<audio-files/>
	<image-files/>
	<other-files/>
	<text-files/>
	<video-files/>
</action>
'''
    open(p, "w").write(s.replace("</actions>", act + "</actions>"))
a = os.path.expanduser("~/.config/Thunar/accels.scm")
line = f'(gtk_accel_path "<Actions>/ThunarActions/uca-action-{uid}" "space")\n'
cur = open(a).read() if os.path.exists(a) else ""
if line not in cur:
    open(a, "a").write("\n" + line)
EOF
  (setsid thunar --daemon >/dev/null 2>&1 &)
}

# --------------------------------------- tela de bloqueio + Ctrl+Alt+Q
mod_bloqueio() {
  say "Tela de bloqueio com o papel de parede + atalho Ctrl+Alt+Q"
  sudo pacman -S --needed --noconfirm imagemagick
  local wall dir="$BG/lockscreen" X=xfce4-screensaver
  wall="$(xfconf-query -c xfce4-desktop -lv | awk '/last-image/{print $2; exit}')"
  [ -f "$wall" ] || { echo "Papel de parede não encontrado."; return 1; }
  mkdir -p "$dir"
  # O papel de parede é um padrão pequeno repetido; gera versão do tamanho da tela
  local res; res="$(xrandr | awk '/ current /{gsub(",","");print $8"x"$10}')"
  magick -size "$res" tile:"$wall" "$dir/lock.png"
  xfconf-query -c $X -p /saver/mode -n -t int -s 2
  xfconf-query -c $X -p /saver/themes/list -n -t string -a -s xfce-personal-slideshow.desktop
  xfconf-query -c $X -p /screensavers/xfce-personal-slideshow/arguments -n -t string \
    -s "--location=$dir --background-color=#000000"
  xfconf-query -c $X -p /lock/enabled -n -t bool -s true
  xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/<Primary><Alt>q" -n -t string -s xflock4
}

# ------------------------------------------------ engenharia de computação
mod_dev() {
  say "Ferramentas de engenharia de computação (repositórios oficiais)"
  # Obs.: não inclui 'code' (conflita com visual-studio-code-bin do AUR).
  sudo pacman -S --needed --noconfirm \
    base-devel git gdb valgrind cmake clang nasm \
    python-pip python-numpy python-scipy python-matplotlib jupyter-notebook octave \
    nodejs npm jdk-openjdk go rustup \
    iverilog gtkwave verilator \
    avr-gcc avr-libc avrdude arm-none-eabi-gcc arm-none-eabi-newlib openocd \
    arduino-cli minicom picocom kicad qemu-desktop sqlite wireshark-qt \
    texlive-latex texlive-latexextra texlive-langportuguese texlive-bibtexextra \
    texlive-fontsrecommended texlive-binextra
  rustup default stable || true
}

# ---------------------------------------------------------------- ventoinha
# fan-modo: alterna entre 'sala' (ventoinha parada até ser obrigatório ligar),
# 'normal' (teto no nível 4) e 'max'. Requer thinkfan configurado no ThinkPad.
mod_fan() {
  say "Instalando fan-modo (use: fan-modo sala | normal | max | -w)"
  mkdir -p "$BIN"
  install -m 755 "$HERE/fan-modo.py" "$BIN/fan-modo"
  command -v thinkfan >/dev/null || echo "Aviso: thinkfan não instalado (sudo pacman -S thinkfan)."
}

# ---------------------------------------------------- computador de estudante
# Backup do sistema (Timeshift/rsync), firewall, Docker com dados em /home,
# ferramentas de terminal e grupos do usuário. REINICIE depois: firewall e Docker
# dependem dos módulos do kernel em uso, e os grupos só valem após novo login.
mod_estudante() {
  say "Pacotes: timeshift, ufw, docker, ferramentas de terminal"
  sudo pacman -Syu --noconfirm --needed timeshift rsync cronie ufw docker docker-compose docker-buildx \
    tmux fzf ripgrep fd btop tree uv python-pipx nmap radare2 bear ccache neovim

  say "Firewall (ufw): nega entrada, permite saída"
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo sed -i 's/^ENABLED=.*/ENABLED=yes/' /etc/ufw/ufw.conf
  sudo systemctl enable --now ufw || echo "ufw sobe após reiniciar (módulos do kernel)"

  say "Docker com dados em /home/docker (evita encher a / de 32 GB)"
  sudo mkdir -p /etc/docker /home/docker
  printf '{\n  "data-root": "/home/docker"\n}\n' | sudo tee /etc/docker/daemon.json >/dev/null
  sudo systemctl enable --now docker || echo "docker sobe após reiniciar"

  say "Grupos do usuário: docker (equivale a root!), uucp (serial/Arduino), wireshark"
  for g in docker uucp wireshark; do getent group "$g" >/dev/null && sudo usermod -aG "$g" "$USER"; done

  say "Timeshift: snapshots semanais do sistema na partição /home"
  sudo systemctl enable --now cronie
  local uuid; uuid="$(findmnt -no UUID /home)"
  sudo mkdir -p /etc/timeshift
  sudo tee /etc/timeshift/timeshift.json >/dev/null <<JSON
{
  "backup_device_uuid" : "$uuid",
  "parent_device_uuid" : "",
  "do_first_run" : "false",
  "btrfs_mode" : "false",
  "include_btrfs_home_for_backup" : "false",
  "include_btrfs_home_for_restore" : "false",
  "stop_cron_emails" : "true",
  "schedule_monthly" : "false",
  "schedule_weekly" : "true",
  "schedule_daily" : "false",
  "schedule_hourly" : "false",
  "schedule_boot" : "false",
  "count_monthly" : "2",
  "count_weekly" : "3",
  "count_daily" : "5",
  "count_hourly" : "6",
  "count_boot" : "5",
  "snapshot_size" : "0",
  "snapshot_count" : "0",
  "date_format" : "%Y-%m-%d %H:%M:%S",
  "exclude" : [],
  "exclude-apps" : []
}
JSON
  echo "Primeiro snapshot: sudo timeshift --create --comments 'inicial'"
  echo "Aviso: o snapshot fica no MESMO disco físico; copie seus arquivos para um HD externo ou nuvem."
  rustup default stable || true
}

# ------------------------------------------------------------------ impressora
# CUPS + descoberta por mDNS + scanner. Adiciona a primeira impressora IPP achada na
# rede (sem driver, IPP Everywhere). Rode com a impressora ligada na mesma rede.
mod_impressao() {
  say "Serviços de impressão (CUPS, Avahi/mDNS, SANE)"
  sudo pacman -S --needed --noconfirm cups cups-filters ghostscript cups-pk-helper \
    system-config-printer avahi nss-mdns sane sane-airscan ipp-usb gutenprint
  sudo cp -n /etc/nsswitch.conf /etc/nsswitch.conf.bak-mdns
  grep -q mdns_minimal /etc/nsswitch.conf || sudo sed -i \
    's/^hosts: mymachines resolve \[!UNAVAIL=return\]/hosts: mymachines mdns_minimal [NOTFOUND=return] resolve [!UNAVAIL=return]/' /etc/nsswitch.conf
  sudo systemctl enable --now avahi-daemon cups.socket cups.path cups
  sudo ufw allow 5353/udp comment 'mDNS descoberta de impressoras' 2>/dev/null || true
  sudo ufw allow 631/tcp comment 'IPP' 2>/dev/null || true

  say "Procurando impressoras IPP na rede"
  local linha ip nome
  linha="$(timeout 10 avahi-browse -rtp _ipp._tcp 2>/dev/null | grep '^=;' | grep ';IPv4;' | head -1)"
  [ -n "$linha" ] || { echo "Nenhuma impressora achada. Ligue-a na mesma rede e rode de novo."; return 0; }
  ip="$(echo "$linha" | cut -d';' -f8)"
  nome="$(echo "$linha" | cut -d';' -f4 | sed 's/\\032/_/g; s/[^A-Za-z0-9_]//g')"
  echo "Achada: $nome em $ip"
  sudo lpadmin -p "$nome" -E -v "ipp://$ip/ipp/print" -m everywhere -o media-default=iso_a4_210x297mm
  sudo lpoptions -d "$nome"
  echo "Pronto. Página de teste: lp -d $nome /usr/share/cups/data/testprint"
}

# `scanimage -L` com sane-airscan devolveu a página web da HP; este comando fala eSCL direto.
mod_escanear() {
  say "Instalando 'escanear' em $BIN"
  mkdir -p "$BIN"
  install -m 755 "$HERE/escanear.py" "$BIN/escanear"
}

# ------------------------------------------------- Claude Desktop: barra do sistema
# Edita o app.asar do pacote (troca de texto do mesmo tamanho) e guarda backup em
# ~/.local/share/claude-desktop-backup. Atualizações do app desfazem a edição.
mod_claude_titlebar() {
  say "Instalando 'claude-titlebar' em $BIN (use: claude-titlebar on | off | status)"
  mkdir -p "$BIN"
  install -m 755 "$HERE/claude-titlebar.py" "$BIN/claude-titlebar"
  install -m 755 "$HERE/corretor-claude-off.py" "$BIN/corretor-claude-off"
}

# ------------------------------------------------------------------ Emacs + Doom
mod_emacs() {
  say "Emacs + Doom Emacs"
  sudo pacman -S --needed --noconfirm emacs ripgrep fd git ttf-jetbrains-mono \
    ttf-nerd-fonts-symbols-mono noto-fonts-emoji shellcheck discount
  if [ ! -d "$HOME/.config/emacs" ]; then
    git clone --depth 1 https://github.com/doomemacs/doomemacs "$HOME/.config/emacs"
    "$HOME/.config/emacs/bin/doom" install --force --config --env --install
  fi
  command -v fish >/dev/null && fish -c 'fish_add_path ~/.config/emacs/bin' || true
  # fonte legível (o monospace padrão, Nimbus Mono PS, fica serrilhado com hintfull)
  grep -q 'JetBrains Mono' "$HOME/.config/doom/config.el" 2>/dev/null || cat >> "$HOME/.config/doom/config.el" <<'ELISP'

;; Fonte: JetBrains Mono em vez do monospace padrão do sistema
(setq doom-font (font-spec :family "JetBrains Mono" :size 14)
      doom-variable-pitch-font (font-spec :family "Liberation Sans" :size 14))
ELISP
  "$HOME/.config/emacs/bin/doom" sync
}

MODULES=(eduroam_diag eduroam_senha minecraft tlauncher steam energia boot limpeza xfce idioma corretor_off quicklook bloqueio dev fan estudante impressao escanear claude_titlebar emacs)

if [ $# -eq 0 ]; then
  echo "Módulos: ${MODULES[*]//_/-}"
  echo "Uso: $0 <módulo>... | all"
  exit 0
fi

for m in "$@"; do
  if [ "$m" = all ]; then
    for x in "${MODULES[@]}"; do
      case "$x" in eduroam_senha|tlauncher) continue ;; esac   # exigem ação manual
      "mod_$x"
    done
  else
    "mod_${m//-/_}"
  fi
done
echo; echo "Concluído."
