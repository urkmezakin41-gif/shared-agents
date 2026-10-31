#!/usr/bin/env python3
"""
scripts/bugbounty/ingest.py — pipeline tetikleyici adım.

Zamanlanmış görev tarafından periyodik olarak çalıştırılır. Tek giriş
kanalı: incoming/*.json — git push ile bırakılan ham veri dosyaları.

NOT: Telegram inbound (getUpdates) kasıtlı olarak KULLANILMIYOR. Sebep:
getUpdates tek tüketicili bir API — aynı bot token'ını A14 tarafı da
dinlerse (kendi toplayıcı/hakem akışı için) mesajları birbirinin elinden
kapar. Bu yüzden veri girişi yalnızca incoming/ (git push) üzerinden;
Telegram bu pipeline'da yalnızca ÇIKIŞ (dispatch.py --notify ile
sendDocument, tek yönlü, getUpdates'e dokunmaz) için kullanılıyor.

ZORUNLU alan: "scope_declaration" (boş/çok kısa olamaz). Yoksa dosya
REJECTED olarak işaretlenir, analiz edilmez, veri icat edilmez.

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
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
INCOMING_DIR = REPO_ROOT / "incoming"
PROCESSED_DIR = INCOMING_DIR / "processed"
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


def main():
    ap = argparse.ArgumentParser()
    ap.parse_args()

    pending, rejected = process_incoming_folder()

    manifest = {
        "pending_targets": sorted(set(pending)),
        "rejected": rejected,
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
