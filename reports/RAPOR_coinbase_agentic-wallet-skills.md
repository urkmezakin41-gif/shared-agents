# Bug Bounty Raporu — coinbase_agentic-wallet-skills

**Tarih:** 2026-11-03 00:38 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/agentic-wallet-skills, 'npx skills add' ile kurulan AI agent skill paketi).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_agentic-wallet-skills/raw`
* **Engellenen/erişilemeyen adımlar:** Bu turda yalnizca README.md ve scripts/bump-awal.js geldi; asil skills/ icerigi (SKILL.md/awal paketinin kendisi) gelmedi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* scripts/bump-awal.js: npm registry'den ('https://registry.npmjs.org/awal/latest', SABIT URL) en son surumu cekip skills/ altindaki .md dosyalarinda 'awal@X.Y.Z' referanslarini guncelleyen basit bir bakim script'i. subprocess/exec/eval YOK, yalnizca dosya okuma/yazma + sabit bir HTTPS GET + regex degistirme. Enjeksiyon veya kod calistirma riski yok; bu script GELISTIRICININ KENDI makinesinde elle calistirilan bir araç, disaridan erisilebilir degil.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._