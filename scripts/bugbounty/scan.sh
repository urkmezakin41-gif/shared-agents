#!/usr/bin/env bash
# scripts/bugbounty/scan.sh
#
# Manuel, tek seferlik, PASİF keşif script'i (pipeline'ın tetikleyici
# adımı — bkz. scripts/bugbounty/PIPELINE.md). Bug bounty / AppSec
# denetimi için ham veri toplar; analiz ve triyaj kararını
# recon-and-auditor (Stage 1) + skeptical-triager (Stage 2) agent'ları,
# nihai rapor dosyasını dispatch.py (Stage 3) üretir.
#
# Bu script:
#   - Otomatik/periyodik ÇALIŞMAZ. Her çalıştırma elle tetiklenir.
#   - Yetki/scope beyanı ZORUNLUDUR (--scope). Beyan yoksa çalışmaz.
#   - Yalnızca pasif HTTP GET / DNS sorguları yapar; exploit/DoS göndermez.
#   - Ağ politikası bir host'u engellerse veri İCAT ETMEZ; "BLOCKED" olarak
#     kaydeder.
#   - Telegram'a gönderim sadece --notify bayrağı AÇIKÇA verilirse ve
#     TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID ortam değişkenleri varsa olur.
#     Varsayılan: kapalı.
#
# Kullanım:
#   scripts/bugbounty/scan.sh --target example.com \
#       --scope "Kendi sahip olduğum domain / HackerOne programı: acme (acme.com/.well-known/security.txt)" \
#       [--github owner/repo] [--notify]
#
set -u -o pipefail

TARGET=""
SCOPE=""
GH_REPO=""
NOTIFY=0

usage() {
  cat <<'EOF'
Kullanım: scan.sh --target <domain|owner/repo> --scope "<yetki açıklaması>" [--github owner/repo] [--notify]

  --target   Zorunlu. Taranacak domain (örn: example.com).
  --scope    Zorunlu. Bu hedef için yetki/izin kanıtı (kendi mülkiyeti,
             program adı/URL'si, sözleşme referansı). Boş/varsayımsal
             beyan kabul edilmez.
  --github   Opsiyonel. owner/repo formatında, son commit diff'lerini
             (GitHub public API ile) çekmek için.
  --notify   Opsiyonel. Rapor sonunda TELEGRAM_BOT_TOKEN ve
             TELEGRAM_CHAT_ID ortam değişkenleri varsa ham veri paketini
             Telegram'a gönderir. Varsayılan: kapalı (yalnızca repo
             içine kaydedilir).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    --github) GH_REPO="$2"; shift 2 ;;
    --notify) NOTIFY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Bilinmeyen argüman: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "HATA: --target zorunlu." >&2; usage; exit 2
fi
if [[ -z "$SCOPE" ]]; then
  echo "HATA: --scope zorunlu. Bu hedef için yetki/izin kanıtı belirtmeden tarama yapılmaz." >&2
  usage
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$SCRIPT_DIR/out/$TARGET/raw"
mkdir -p "$OUT_DIR"

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
META_FILE="$OUT_DIR/_meta.json"
LOG_FILE="$OUT_DIR/_scan.log"
: > "$LOG_FILE"

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG_FILE" >&2; }

log "Hedef: $TARGET"
log "Scope beyanı: $SCOPE"

cat > "$META_FILE" <<EOF
{
  "target": "$TARGET",
  "scope_declaration": $(printf '%s' "$SCOPE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
  "started_at": "$TS",
  "github_repo": "$GH_REPO"
}
EOF

CURL_OPTS=(-sS -m 20 --max-redirs 3)

fetch() {
  # fetch <url> <outfile> -> ham veri veya BLOCKED/ERROR kaydı
  local url="$1" out="$2"
  local code
  code=$(curl "${CURL_OPTS[@]}" -o "$out" -w '%{http_code}' "$url" 2>>"$LOG_FILE") || code="000"
  if [[ "$code" == "000" ]]; then
    echo "BLOCKED_OR_UNREACHABLE url=$url" > "$out"
    log "BLOCKED/UNREACHABLE: $url"
    return 1
  fi
  log "OK ($code): $url"
  echo "$code"
  return 0
}

# 1) crt.sh ile alt alan adı keşfi (pasif, sertifika şeffaflık logu)
log "== crt.sh alt alan adı sorgusu =="
fetch "https://crt.sh/?q=%25.$TARGET&output=json" "$OUT_DIR/crtsh_subdomains.json"

# 2) CNAME kayıtları (DNS-over-HTTPS, pasif sorgu)
log "== CNAME sorgusu (DoH) =="
fetch "https://cloudflare-dns.com/dns-query?name=$TARGET&type=CNAME" "$OUT_DIR/cname_${TARGET}.json"
if [[ -s "$OUT_DIR/crtsh_subdomains.json" ]] && ! grep -q BLOCKED_OR_UNREACHABLE "$OUT_DIR/crtsh_subdomains.json"; then
  python3 - "$OUT_DIR/crtsh_subdomains.json" <<'PYEOF' 2>>"$LOG_FILE" || true
import json, sys
try:
    data = json.load(open(sys.argv[1]))
    names = sorted({row.get("name_value", "").strip() for row in data if row.get("name_value")})
    print("\n".join(names))
except Exception as e:
    print(f"PARSE_ERROR: {e}", file=sys.stderr)
PYEOF
fi

# 3) Hedef ana sayfa + .js paket / endpoint keşfi (pasif GET)
log "== Ana sayfa ve JS keşfi =="
fetch "https://$TARGET/" "$OUT_DIR/homepage.html"
if ! grep -q BLOCKED_OR_UNREACHABLE "$OUT_DIR/homepage.html" 2>/dev/null; then
  grep -oE '(src|href)="[^"]*\.js[^"]*"' "$OUT_DIR/homepage.html" 2>/dev/null \
    | sed -E 's/^(src|href)="//; s/"$//' | sort -u > "$OUT_DIR/js_links.txt" || true
  JS_COUNT=$(wc -l < "$OUT_DIR/js_links.txt" 2>/dev/null || echo 0)
  log "Bulunan .js referansı: $JS_COUNT"
  : > "$OUT_DIR/js_endpoints_grep.txt"
  while IFS= read -r js; do
    [[ -z "$js" ]] && continue
    case "$js" in
      http*) jsurl="$js" ;;
      //*) jsurl="https:$js" ;;
      /*) jsurl="https://$TARGET$js" ;;
      *) jsurl="https://$TARGET/$js" ;;
    esac
    jsfile="$OUT_DIR/js_$(echo "$jsurl" | md5sum | cut -d' ' -f1).js"
    fetch "$jsurl" "$jsfile" >/dev/null || continue
    echo "# SOURCE: $jsurl" >> "$OUT_DIR/js_endpoints_grep.txt"
    grep -oE '"(https?:)?/[a-zA-Z0-9_/\.\-]*(api|admin|internal|webhook|callback|proxy)[a-zA-Z0-9_/\.\-]*"' "$jsfile" 2>/dev/null \
      >> "$OUT_DIR/js_endpoints_grep.txt" || true
  done < "$OUT_DIR/js_links.txt"
fi

# 4) GitHub public API ile son commit diff'leri (opsiyonel, salt-okunur)
if [[ -n "$GH_REPO" ]]; then
  log "== GitHub son commit'ler: $GH_REPO =="
  AUTH_HEADER=()
  [[ -n "${GITHUB_TOKEN:-}" ]] && AUTH_HEADER=(-H "Authorization: Bearer $GITHUB_TOKEN")
  code=$(curl "${CURL_OPTS[@]}" "${AUTH_HEADER[@]}" -o "$OUT_DIR/github_commits.json" \
    -w '%{http_code}' "https://api.github.com/repos/$GH_REPO/commits?per_page=5" 2>>"$LOG_FILE") || code="000"
  log "GitHub API HTTP: $code"
  if [[ "$code" == "200" ]]; then
    SHAS=$(python3 -c "import json;print('\n'.join(c['sha'] for c in json.load(open('$OUT_DIR/github_commits.json'))[:3]))" 2>>"$LOG_FILE" || true)
    : > "$OUT_DIR/github_diffs.patch"
    for sha in $SHAS; do
      curl "${CURL_OPTS[@]}" "${AUTH_HEADER[@]}" -H "Accept: application/vnd.github.v3.diff" \
        "https://api.github.com/repos/$GH_REPO/commits/$sha" >> "$OUT_DIR/github_diffs.patch" 2>>"$LOG_FILE" || true
      echo -e "\n---\n" >> "$OUT_DIR/github_diffs.patch"
    done
  else
    echo "BLOCKED_OR_ERROR http=$code" > "$OUT_DIR/github_commits.json"
  fi
fi

log "== Toplama tamamlandı. Ham veri: $OUT_DIR =="
echo "$OUT_DIR"

if [[ "$NOTIFY" == "1" ]]; then
  if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    ARCHIVE="$SCRIPT_DIR/out/${TARGET}_raw_$(date -u +%Y%m%d%H%M%S).tar.gz"
    tar -czf "$ARCHIVE" -C "$OUT_DIR/.." "$(basename "$OUT_DIR")"
    curl -sS -m 30 -F "chat_id=${TELEGRAM_CHAT_ID}" \
      -F "document=@${ARCHIVE}" \
      -F "caption=Ham keşif verisi: ${TARGET} (scope: ${SCOPE})" \
      "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument" \
      -o "$OUT_DIR/_telegram_response.json" -w "\nTelegram HTTP:%{http_code}\n" | tee -a "$LOG_FILE"
  else
    log "UYARI: --notify verildi ama TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID yok; gönderim atlandı."
  fi
fi
