# Bug Bounty Raporu — base_base-snapshots-dashboard

**Tarih:** 2026-11-03 20:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/base-snapshots-dashboard (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_base-snapshots-dashboard/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base node operatorleri icin reth snapshot indirme baglantilarini listeleyen BASIT, salt-okunur bir gosterge paneli -- tek backend uc noktasi (`app/api/snapshots/route.ts`) HICBIR kullanici girdisi (sorgu parametresi, POST govdesi, path parametresi) ALMIYOR; TAMAMEN sabit-kodlanmis `base.org` alt-alan adlarindan ve public JSON-RPC uc noktalarindan (mainnet.base.org, sepolia.base.org) veri cekiyor.
* Son iki commit: (1) 'legacy-full' snapshot turunun kaldirilmasi (yapilandirma degisikligi, mantik etkisi yok); (2) TAMAMEN kozmetik koyu-mod renk-token refaktoru (tailwind.config.ts + page.tsx class adlari) -- guvenlik etkisi SIFIR.
* `app/api/snapshots/route.ts` incelendi: hicbir gizli anahtar/kimlik dogrulama kullanilmiyor (herkese acik bir veri toplayici oldugu icin gerek yok), tum URL'ler SABIT (`SNAPSHOT_CONFIGS` dizisinde statik olarak tanimli, kullanicidan gelen hicbir degerle BIRLESTIRILMIYOR) -- SSRF/path-traversal/enjeksiyon icin bir yuzey YOK.
* Genel tarama: dangerouslySetInnerHTML, eval, process.env kullanimi (sir yok) icin tum dosyalar grep edildi -- hicbiri bulunamadi.
* SONUC: Bu, dogasi geregi SIFIR kullanici-girdisi yuzeyine sahip, basit bir salt-okunur veri-toplayici gosterge paneli -- PASS veya hint-tier seviyesinde raporlanabilir bir guvenlik acigi TESPIT EDILEMEDI. Temiz rapor (findings=[]) teslim ediliyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._