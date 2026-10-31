#!/usr/bin/env python3
"""
scripts/bugbounty/ingest.py — pipeline tetikleyici adım, 2 kanal.

Zamanlanmış görev tarafından periyodik olarak çalıştırılır. İki kanalı
kontrol eder:
  A) incoming/*.json  — git push ile bırakılan ham veri dosyaları
  B) Telegram getUpdates — TELEGRAM_BOT_TOKEN varsa, bota gönderilen
     belgeler (aynı JSON şemasıyla)

Her ikisi için de ZORUNLU alan: "scope_declaration" (boş/çok kısa olamaz).
Yoksa dosya/mesaj REJECTED olarak işaretlenir, analiz edilmez, veri
icat edilmez.

Geçerli her öğe için scripts/bugbounty/out/<target>/raw/ altına ham
veriyi yazar ve stdout'a bir JSON manifest basar:

  {"pending_targets": ["example.com", ...], "rejected": [{"source":..., "reason":...}]}

Bu script YALNIZCA veri hazırlar; Stage 1/2 (LLM analiz/triyaj) ve
Stage 3 (dispatch.py) BU SCRIPT TARAFINDAN ÇAĞRILMAZ — onları, bu
scripti çalıştıran oturum (Claude), manifest'teki her pending_target
için ayrı ayrı yürütür (bkz. scripts/bugbounty/PIPELINE.md).
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
INCOMING_DIR = REPO_ROOT / "incoming"
PROCESSED_DIR = INCOMING_DIR / "processed"
STATE_DIR = SCRIPT_DIR / ".state"
TELEGRAM_OFFSET_FILE = STATE_DIR / "telegram_offset.txt"
MIN_SCOPE_LEN = 5


def validate_and_stage(payload: dict, source_label: str) -> tuple[bool, str]:
    """Doğrular, geçerliyse ham veriyi out/<target>/raw/'a yazar.
    Döner: (kabul_edildi_mi, sebep_veya_target)"""
    target = (payload.get("target") or "").strip()
    scope = (payload.get("scope_declaration") or "").strip()
    raw = payload.get("raw") or {}

    if not target:
        return False, "target alanı eksik"
    if len(scope) < MIN_SCOPE_LEN:
        return False, "scope_declaration eksik veya çok kısa (zorunlu yetki beyanı yok)"
    if not raw or not any(raw.values()):
        return False, "raw veri boş, analiz edilecek bir şey yok"

    out_raw_dir = SCRIPT_DIR / "out" / target / "raw"
    out_raw_dir.mkdir(parents=True, exist_ok=True)
    dest = out_raw_dir / f"ingested_{source_label.replace('/', '_')}.json"
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    meta_path = out_raw_dir / "_meta.json"
    meta_path.write_text(json.dumps({
        "target": target,
        "scope_declaration": scope,
        "source": source_label,
        "ingested_via": "ingest.py",
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return True, target


def process_incoming_folder() -> tuple[list[str], list[dict]]:
    pending, rejected = [], []
    if not INCOMING_DIR.exists():
        return pending, rejected
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for f in sorted(INCOMING_DIR.glob("*.json")):
        try:
            payload = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            dest = PROCESSED_DIR / f"REJECTED_parse_error_{f.name}"
            f.rename(dest)
            rejected.append({"source": f.name, "reason": f"JSON parse hatası: {e}"})
            continue

        ok, result = validate_and_stage(payload, f"incoming/{f.stem}")
        if ok:
            dest = PROCESSED_DIR / f"OK_{f.name}"
            f.rename(dest)
            pending.append(result)
        else:
            safe_reason = result.replace(" ", "_")[:40]
            dest = PROCESSED_DIR / f"REJECTED_{safe_reason}_{f.name}"
            f.rename(dest)
            rejected.append({"source": f.name, "reason": result})

    return pending, rejected


def process_telegram() -> tuple[list[str], list[dict]]:
    pending, rejected = [], []
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return pending, rejected

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    last_offset = 0
    if TELEGRAM_OFFSET_FILE.exists():
        try:
            last_offset = int(TELEGRAM_OFFSET_FILE.read_text().strip() or "0")
        except ValueError:
            last_offset = 0

    try:
        result = subprocess.run(
            ["curl", "-sS", "-m", "20",
             f"https://api.telegram.org/bot{token}/getUpdates?offset={last_offset + 1}&timeout=0"],
            capture_output=True, text=True, timeout=25,
        )
        updates = json.loads(result.stdout).get("result", [])
    except Exception as e:
        print(f"[ingest] Telegram getUpdates başarısız: {e}", file=sys.stderr)
        return pending, rejected

    max_update_id = last_offset
    for upd in updates:
        max_update_id = max(max_update_id, upd.get("update_id", 0))
        msg = upd.get("message") or {}
        doc = msg.get("document")
        if not doc:
            continue  # yalnızca belge (JSON dosyası) ekli mesajları işliyoruz
        file_id = doc.get("file_id")
        source_label = f"telegram/{upd.get('update_id')}"
        try:
            gf = subprocess.run(
                ["curl", "-sS", "-m", "20",
                 f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"],
                capture_output=True, text=True, timeout=25,
            )
            file_path = json.loads(gf.stdout)["result"]["file_path"]
            dl = subprocess.run(
                ["curl", "-sS", "-m", "20",
                 f"https://api.telegram.org/file/bot{token}/{file_path}"],
                capture_output=True, text=True, timeout=25,
            )
            payload = json.loads(dl.stdout)
        except Exception as e:
            rejected.append({"source": source_label, "reason": f"indirme/parse hatası: {e}"})
            continue

        ok, result = validate_and_stage(payload, source_label)
        if ok:
            pending.append(result)
        else:
            rejected.append({"source": source_label, "reason": result})

    if max_update_id > last_offset:
        TELEGRAM_OFFSET_FILE.write_text(str(max_update_id), encoding="utf-8")

    return pending, rejected


def main():
    ap = argparse.ArgumentParser()
    ap.parse_args()

    p1, r1 = process_incoming_folder()
    p2, r2 = process_telegram()

    manifest = {
        "pending_targets": sorted(set(p1 + p2)),
        "rejected": r1 + r2,
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
