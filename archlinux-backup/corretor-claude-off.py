#!/usr/bin/env python3
import json, os, shutil, subprocess, time
p = os.path.expanduser("~/.config/Claude/Preferences")
while subprocess.run(["pgrep", "-f", "/usr/lib/claude-desktop"], capture_output=True).returncode == 0:
    time.sleep(2)
shutil.copy(p, p + ".bak-spell")
d = json.load(open(p))
d.setdefault("browser", {})["enable_spellchecking"] = False
d.setdefault("spellcheck", {})["dictionaries"] = []
d["spellcheck"]["dictionary"] = ""
json.dump(d, open(p, "w"), separators=(",", ":"))
