# common/management/commands/autotranslate_po_offline.py
from __future__ import annotations
import re, time
from pathlib import Path
from typing import Dict, Tuple, List

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import polib

# Argos Translate (offline)
from argostranslate import package, translate as argos_translate

# Protect gettext placeholders like "%(name)s", "%s", "%d", "%.2f"
PH_RE = re.compile(r"%\([^)]+\)s|%s|%d|%(\.\d+)?f")

LANGS = ["ru", "pl", "tr"]
SRC = "en"

def mask_placeholders(text: str) -> Tuple[str, Dict[str, str]]:
    repl: Dict[str, str] = {}
    def _sub(m):
        token = f"<<P{len(repl)}>>"
        repl[token] = m.group(0)
        return token
    return PH_RE.sub(_sub, text), repl

def unmask(text: str, repl: Dict[str, str]) -> str:
    for token, original in repl.items():
        text = text.replace(token, original)
    return text

def ensure_argos_model(src: str, tgt: str) -> None:
    # Install en->tgt if missing
    installed = package.get_installed_packages()
    if any(p.from_code == src and p.to_code == tgt for p in installed):
        return
    package.update_package_index()
    available = package.get_available_packages()
    # prefer exact en->tgt
    for p in available:
        if p.from_code == src and p.to_code == tgt:
            pkg_path = p.download()
            package.install_from_path(pkg_path)
            return
    raise CommandError(f"No Argos model found for {src}->{tgt}")

def argos_translate_text(text: str, src: str, tgt: str) -> str:
    # Argos works per-string; we mask placeholders to keep them intact.
    masked, repl = mask_placeholders(text)
    out = argos_translate.translate(masked, src, tgt)
    return unmask(out, repl)

class Command(BaseCommand):
    help = "Offline auto-translate empty msgstr in locale/*/LC_MESSAGES/django.po using Argos Translate."

    def add_arguments(self, parser):
        parser.add_argument("--langs", nargs="+", default=LANGS, help="Target languages (default: ru pl tr)")
        parser.add_argument("--source", default=SRC, help="Source language (default: en)")
        parser.add_argument("--dry-run", action="store_true", help="Do not write changes")
        parser.add_argument("--sleep", type=float, default=0.0, help="Sleep seconds between strings (optional)")

    def handle(self, *args, **opts):
        src = opts["source"].split("-")[0]
        targets = [l.split("-")[0] for l in opts["langs"]]

        # Where your locale/ lives
        locale_root = Path((getattr(settings, "LOCALE_PATHS", [settings.BASE_DIR / "locale"]))[0])
        if not locale_root.exists():
            raise CommandError(f"Locale dir not found: {locale_root}")

        # Ensure Argos models are ready (one-time download per pair)
        for t in targets:
            self.stdout.write(f"Ensuring Argos model {src}->{t} …")
            ensure_argos_model(src, t)

        total = 0
        for t in targets:
            po_path = locale_root / t / "LC_MESSAGES" / "django.po"
            if not po_path.exists():
                self.stdout.write(self.style.WARNING(f"Missing {po_path}, skipping"))
                continue

            po = polib.pofile(str(po_path), encoding="utf-8")

            changed = 0
            for entry in po:
                if entry.obsolete:
                    continue

                # plural entries
                if entry.msgid_plural:
                    # Fill each plural form if empty:
                    for idx_key, current in entry.msgstr_plural.items():
                        if current.strip():
                            continue
                        # index 0 ~ singular; others ~ plural text (best-effort)
                        src_text = entry.msgid if int(idx_key) == 0 else entry.msgid_plural
                        translated = argos_translate_text(src_text, src, t)
                        if not opts["dry_run"]:
                            entry.msgstr_plural[idx_key] = translated
                        changed += 1
                        if opts["sleep"]: time.sleep(opts["sleep"])
                    continue

                # single entries
                if not entry.msgstr.strip():
                    entry.msgstr = argos_translate_text(entry.msgid, src, t) if not opts["dry_run"] else entry.msgstr
                    changed += 1
                    if opts["sleep"]: time.sleep(opts["sleep"])

            if changed and not opts["dry_run"]:
                po.save(str(po_path))
                self.stdout.write(self.style.SUCCESS(f"{t}: filled {changed} entries"))
                total += changed
            else:
                self.stdout.write(f"{t}: nothing to translate.")

        if total and not opts["dry_run"]:
            self.stdout.write("Compiling .mo files …")
            # call compilemessages (uses your current Python)
            import sys, os
            os.system(f'"{sys.executable}" "{settings.BASE_DIR / "manage.py"}" compilemessages')

        self.stdout.write(self.style.SUCCESS(f"Done. Total filled: {total}"))
