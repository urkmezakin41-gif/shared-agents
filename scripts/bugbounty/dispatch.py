#!/usr/bin/env python3
"""
scripts/bugbounty/dispatch.py — Pipeline Stage 3 (deterministic gate).

Stage 1 (recon-and-auditor) ve Stage 2 (skeptical-triager) ajanlarının
ürettiği JSON dosyalarını birleştirir ve YALNIZCA confidence >= 90 VE
verdict == "PASS" olan bulguları reports/RAPOR_<target>.md'ye yazar.

Bilinçli olarak YAPMADIKLARI:
  - GitHub Private Vulnerability Reporting API'sine otomatik gönderim yok.
  - HackerOne API'sine otomatik gönderim yok.
  (Bkz. .claude/agents/report-dispatcher.md — gerekçe orada.)

Yaptıkları:
  - reports/RAPOR_<target>.md yazar (kopyala-yapıştır'a hazır İngilizce
    taslak dahil, yalnızca geçen bulgular için).
  - --notify verildiyse VE TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID ortam
    değişkenleri varsa, üretilen raporu Telegram'a "gözden geçirme için"
    dosya olarak gönderir (bu resmi bir submission değildir).

Kullanım:
  python3 scripts/bugbounty/dispatch.py --target <hedef> [--notify] [--threshold 90]
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PASS_THRESHOLD_DEFAULT = 0


def load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_report(target: str, stage1: dict, passed: list[dict], rejected: list[dict], threshold: int) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    scope = stage1.get("scope_declaration", "(belirtilmemiş)")
    blocked = stage1.get("blocked_or_unreachable_steps") or []
    skipped_no_reward = stage1.get("skipped_no_reward") or []

    lines = []
    lines.append(f"# Bug Bounty Raporu — {target}")
    lines.append("")
    lines.append(f"**Tarih:** {ts}")
    lines.append(f"**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher")
    lines.append(f"**Gönderim eşiği:** verdict == PASS (Claude Karar?)")
    lines.append("")
    lines.append("## 📦 0. Yetki/Scope Kaydı")
    lines.append(f"* **Beyan edilen yetki:** {scope}")
    lines.append(f"* **Ham veri kaynağı:** `{stage1.get('raw_data_dir', 'N/A')}`")
    if blocked:
        lines.append(f"* **Engellenen/erişilemeyen adımlar:** {', '.join(blocked)}")
    else:
        lines.append("* **Engellenen/erişilemeyen adımlar:** yok")
    if skipped_no_reward:
        lines.append("")
        lines.append("### Ödül Dışı Olarak Atlanan Konular")
        for note in skipped_no_reward:
            lines.append(f"* [ÖDÜL DEĞERİ YOK - ATLANDI] {note}")

    analyst_notes = stage1.get("analyst_notes_tr") or []
    if analyst_notes:
        lines.append("")
        lines.append("### 📓 Analist Notları (bulgu değil, ama kayda değer)")
        lines.append(
            "_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt "
            "eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık "
            "için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla "
            "yeniden değerlendirilebilir._"
        )
        for note in analyst_notes:
            lines.append(f"* {note}")
    lines.append("")

    if not passed:
        lines.append("## 📊 1. HIZLI TRİYAJ KARARI")
        lines.append("* **Durum:** `[⚪ TEMİZ - GEÇ]`")
        lines.append(f"* **Not:** Stage 1, {len(stage1.get('findings', []))} aday bulgu üretti; "
                      f"bunlardan hiçbiri Stage 2'nin ≥{threshold} confidence eşiğini geçemedi.")
        lines.append("")
    else:
        for f in passed:
            v = f["_verdict"]
            lines.append(f"## 📊 Bulgu {f['id']}: {f.get('title', '(başlıksız)')}")
            lines.append(f"* **Durum:** `[🚨 KRİTİK BULGU]`" if f.get("severity_estimate") == "Critical"
                          else "* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`")
            lines.append(f"* **Tahmini Önem Derecesi:** {f.get('severity_estimate', 'N/A')}")
            lines.append(f"* **Zafiyet Sınıfı (CWE):** {f.get('cwe', 'N/A')}")
            lines.append(f"* **Stage 2 Confidence:** {v['confidence']}/100 — {v.get('reason', '')}")
            lines.append("")
            lines.append("### 🔍 Teknik Kanıt ve Kod Analizi")
            lines.append(f"* **Sorunlu Dosya / Uç Nokta / Satır:** {f.get('location', 'N/A')}")
            lines.append(f"* **Kanıt kaynağı:** `{f.get('evidence_source_file', 'N/A')}`")
            lines.append(f"* **Kanıt alıntısı:**\n  ```\n  {f.get('evidence_quote', '')}\n  ```")
            lines.append(f"* **Neden Güvenlik Açığı Oluşuyor?:** {f.get('why_vulnerable_tr', 'N/A')}")
            steps = f.get("safe_verification_steps_tr") or []
            if steps:
                lines.append("* **Nasıl Doğrulanır (Güvenli Doğrulama Adımları):**")
                for i, s in enumerate(steps, 1):
                    lines.append(f"  {i}. {s}")
            lines.append("")
            if f.get("hackerone_draft_en"):
                lines.append("### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)")
                lines.append("")
                lines.append("> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.")
                lines.append("> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.")
                lines.append("")
                lines.append("```markdown")
                lines.append(f.get("hackerone_draft_en", "").rstrip())
                lines.append("```")
                lines.append("")

    if rejected:
        lines.append("## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)")
        lines.append("")
        lines.append("| ID | Confidence | Verdict | Sebep |")
        lines.append("|---|---|---|---|")
        for f in rejected:
            v = f["_verdict"]
            mfiles_str = ", ".join((v.get("missing_files") or f.get("missing_files") or [])[:5])
            lines.append(f"| {f['id']} | {v['confidence']} | {v['verdict']} | {v.get('reason', '')} | {mfiles_str} |")
        lines.append("")

    lines.append("---")
    lines.append(
        "_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. "
        "Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne "
        "API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve "
        "elle yapıştırma gerektirir._"
    )
    return "\n".join(lines)


def send_telegram(report_path: Path, target: str, passed_count: int) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[dispatch] --notify verildi ama TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID yok; atlandı.", file=sys.stderr)
        return
    caption = (
        f"Bug bounty raporu hazır: {target} "
        f"({passed_count} bulgu eşiği geçti). GÖZDEN GEÇİRME İÇİN — "
        f"otomatik olarak hiçbir resmi platforma gönderilmedi."
    )
    cmd = [
        "curl", "-sS", "-m", "30",
        "-F", f"chat_id={chat_id}",
        "-F", f"document=@{report_path}",
        "-F", f"caption={caption}",
        f"https://api.telegram.org/bot{token}/sendDocument",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        print(f"[dispatch] Telegram gönderim denemesi, exit={result.returncode}", file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.returncode != 0 and result.stderr:
            print(result.stderr, file=sys.stderr)
    except Exception as e:
        print(f"[dispatch] Telegram gönderimi başarısız: {e}", file=sys.stderr)


def send_telegram_hints(target: str, hints: list[dict]) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    lines = [f"💡 [İPUCU KATMANI — {target}]", "Hipotez var ama kanıt/dosya eksik (HackerOne'a gönderilmedi):"]
    for f in hints:
        v = f.get("_verdict", {})
        conf = v.get("confidence", 0)
        title = f.get("title", f.get("id", "?"))
        reason = v.get("hint_tr") or v.get("reason", "")
        mfiles = v.get("missing_files") or f.get("missing_files") or []
        lines.append(f"• {f.get('id')} (Güven {conf}): {title} — {reason}")
        if mfiles:
            lines.append(f"  📂 Eksik Dosya: {', '.join(mfiles[:5])}")
    text = "\n".join(lines)[:3900]
    cmd = [
        "curl", "-sS", "-m", "20",
        "-X", "POST",
        f"https://api.telegram.org/bot{token}/sendMessage",
        "-d", f"chat_id={chat_id}",
        "--data-urlencode", f"text={text}",
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--notify", action="store_true",
                     help="Rapor dosyasını Telegram'a GÖZDEN GEÇİRME için gönder (resmi submission değil).")
    ap.add_argument("--threshold", type=int, default=PASS_THRESHOLD_DEFAULT)
    args = ap.parse_args()

    out_dir = SCRIPT_DIR / "out" / args.target
    stage1_path = out_dir / "stage1_findings.json"
    stage2_path = out_dir / "stage2_verdicts.json"

    stage1 = load_json(stage1_path)
    stage2 = load_json(stage2_path)

    if stage1 is None:
        print(f"HATA: {stage1_path} bulunamadı. Önce recon-and-auditor (Stage 1) çalıştırılmalı.", file=sys.stderr)
        sys.exit(2)
    if stage2 is None:
        print(f"HATA: {stage2_path} bulunamadı. Önce skeptical-triager (Stage 2) çalıştırılmalı.", file=sys.stderr)
        sys.exit(2)

    verdicts_by_id = {v["id"]: v for v in stage2.get("verdicts", [])}
    findings = stage1.get("findings", [])

    passed, rejected = [], []
    for f in findings:
        v = verdicts_by_id.get(f["id"])
        if v is None:
            # Stage 2 bu bulguyu hiç değerlendirmemiş -> güvenli taraf: reddet.
            v = {"id": f["id"], "verdict": "REJECT", "confidence": 0,
                 "reason": "Stage 2 tarafından değerlendirilmedi"}
        f = dict(f)
        f["_verdict"] = v
        if v.get("verdict") == "PASS" and v.get("confidence", 0) >= args.threshold:
            passed.append(f)
        else:
            rejected.append(f)

    report_md = render_report(args.target, stage1, passed, rejected, args.threshold)

    repo_root = SCRIPT_DIR.parent.parent
    reports_dir = repo_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"RAPOR_{args.target}.md"
    report_path.write_text(report_md, encoding="utf-8")

    print(f"[dispatch] Yazıldı: {report_path}")
    print(f"[dispatch] Eşiği geçen bulgu: {len(passed)} / Toplam aday: {len(findings)}")

    hints = [
        f for f in rejected
        if f.get("_verdict", {}).get("confidence", 0) >= 15
        or f.get("_verdict", {}).get("missing_files")
        or f.get("missing_files")
    ]
    if args.notify and len(passed) > 0:
        send_telegram(report_path, args.target, len(passed))
    elif args.notify and len(hints) > 0:
        send_telegram_hints(args.target, hints)
    elif args.notify:
        print('[dispatch] Bulgu veya ipucu yok ([TEMIZ - GEC]), Telegram bildirimi atlandi.')

    print(
        "[dispatch] NOT: Hiçbir bulgu GitHub PVR / HackerOne API'sine otomatik "
        "gönderilmedi. Gönderim için raporu inceleyip kendiniz platforma "
        "yapıştırmanız gerekiyor."
    )


if __name__ == "__main__":
    main()
