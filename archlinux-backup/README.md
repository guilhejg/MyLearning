# arch-xfce-setup

Configurações e ferramentas aplicadas num ThinkPad (i5-3230M, Intel HD 4000)
com **Arch Linux + XFCE + NetworkManager**, reunidas num script reproduzível.

## Uso

```bash
./setup.sh                 # lista os módulos
./setup.sh energia xfce    # roda só alguns
./setup.sh all             # todos (menos eduroam-senha e tlauncher, que são manuais)
```

Cada módulo é idempotente. Leia o script antes de rodar: ele usa `sudo`.

## O que cada módulo faz

| Módulo | O que resolve |
|---|---|
| `eduroam-diag` | Instala o diagnóstico de Wi-Fi da eduroam (`eduroam-diag -m 5`) |
| `eduroam-senha` | Grava a senha no perfil `eduroam` (pede em prompt oculto) |
| `minecraft` | Java 8/17 e `xorg-xrandr` (sem ele o Minecraft 1.12.2 cai ao iniciar) |
| `tlauncher` | Extrai o `TLauncher*.zip` baixado e cria o atalho no menu |
| `steam` | Steam via Flatpak + permissão de controles |
| `energia` | TLP com `schedutil`/turbo em vez de `performance` fixo |
| `boot` | Desativa `NetworkManager-wait-online` |
| `limpeza` | `paccache` semanal e limpeza de caches |
| `xfce` | Compositor desligado; suspender ao fechar a tampa |
| `idioma` | Locale `pt_BR.UTF-8` |
| `corretor-off` | Desliga o corretor do Chrome/Claude Desktop e remove o aspell |
| `quicklook` | Espaço no Thunar abre o Sushi (estilo macOS) |
| `bloqueio` | Papel de parede na tela de bloqueio + `Ctrl+Alt+Q` |
| `dev` | Toolchain de engenharia de computação: C/C++, Python científico, Verilog, AVR/ARM, KiCad, LaTeX, etc. (~2 GB de download) |

## `eduroam-diag`

Programa de terminal (só Python 3 + `nmcli`/`iw`/`journalctl`) que diz o que está
acontecendo com a eduroam: sinal/distância do AP, perfil salvo, erros de senha,
certificado, RADIUS, DHCP, e testa gateway/DNS/internet.

```bash
eduroam-diag            # logs da última hora
eduroam-diag -m 5       # só os últimos 5 minutos (logo após uma falha)
```

### Problema que originou tudo

O perfil da eduroam estava sem senha salva, e o NetworkManager falhava com
`no-secrets` (`Secrets were required, but not provided`).

## Observações

- **Nenhuma senha está neste repositório.** `eduroam-senha` pede a senha em tempo de execução.
- A eduroam (e redes institucionais em geral) pode bloquear/interceptar HTTPS de sites
  de jogos; Steam e TLauncher precisam de outra rede para o primeiro download.
- Os módulos que editam `/etc` pedem `sudo`; revise antes de rodar.
