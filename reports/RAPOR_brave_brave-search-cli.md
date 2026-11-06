# Bug Bounty Raporu — brave_brave-search-cli

**Tarih:** 2026-11-06 19:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/brave-search-cli (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Rust. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_brave-search-cli/raw`
* **Engellenen/erişilemeyen adımlar:** `scripts/install.sh` VE `scripts/install.ps1` (curl/irm ILE PIPE-to-shell KURULUM SCRIPT'LERI, KLASIK bir dikkat-GEREKTIREN alan: checksum DOGRULAMASI, HTTPS zorunlulugu, GECICI dosya YONETIMI) bu teslimde TAM dosya icerigi OLARAK YER ALMIYOR (SADECE commit diff'indeki SURUM-numarasi DEGISIKLIGI goruluyor, orn. 'v1.6.0' -> 'v1.7.0') -- TAM script MANTIGI incelenemedi. Kullanim YORUMLARI ('Requires: curl or wget, sha256sum or shasum') bir CHECKSUM DOGRULAMASININ VAR OLDUGUNU ima EDIYOR, ANCAK bu BAGIMSIZ olarak DOGRULANAMADI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine SURUM-bump commit diff'i (1.6.0 -> 1.7.0, CI is akisi/README metin GUNCELLEMELERI) -- kod-MANTIGI degisikligi icermiyor, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Search API icin bir Rust CLI araci ('token-efficient CLI... built for AI agents and LLMs') -- NPM ARACILIGIYLA DAGITILAN bir Node.js SARMALAYICISI (bx.js) ICERIYOR.
* npm/brave-search-cli/bin/bx.js -- platform-OZEL binary'yi npm'in KENDI `optionalDependencies` MEKANIZMASI uzerinden (esbuild/swc GIBI projelerin KULLANDIGI STANDART, GUVENLI desen) COZUYOR -- KENDI BASINA bir URL'den indirme/postinstall SCRIPT'I YOK (README'nin KENDISI 'no postinstall download, works under --ignore-scripts' diyor). `spawnSync(binPath, process.argv.slice(2), {stdio:'inherit'})` bir ARGUMAN DIZISI kullaniyor (shell: true YOK) -- komut-ENJEKSIYONU riski YOK. `require.resolve` SADECE node_modules ICINDEKI BILINEN bir PAKETI COZUYOR, saldirgan-kontrollu bir YOL DEGIL.
* src/config.rs -- API anahtari YONETIMI OLAGANUSTU dikkatli: dosya 0600 izinleriyle, atomik TEMP+rename ile, config dizini 0700 ile SIKILASTIRILARAK yaziliyor; `mask_key()` DIKKATLI bir sekilde ASCII/uzunluk KONTROLU yapip ANCAK sonra byte-indeksleme yapiyor (UTF-8 sinir-PANIGI riski YOK); API anahtari KAYDEDILMEDEN ONCE `validate_api_key()` ile printable-ASCII KONTROLUNDEN GECIYOR.
* src/api.rs -- `agent()`/`streaming_agent()` `max_redirects(0)` AYARLIYOR -- bu, `X-Subscription-Token` (API anahtari) BASLIGININ bir yonlendirme HEDEFINE (potansiyel olarak saldirgan-KONTROLLU bir sunucuya, eger `base_url` BIR GUN kullanici tarafindan KOTU bir deger ile AYARLANIRSA) SIZDIRILMASINI ONLEYEN BILINCLI bir GUVENLIK KARARI. Yanit-govdesi OKUMA, boyut-SINIRLARI (3MB/satir BASI 1MB SSE) ILE KORUNUYOR, UTF-8 sinir-GUVENLI sekilde ISLENIYOR, `BrokenPipe` TEMIZ bir sekilde ELE ALINIYOR. Yalnizca KENDI-URETILEN (NaN/Infinity ASLA uretilmeyecek SEKILDE TASARLANMIS) JSON govdeleri uzerinde `.expect()` KULLANILIYOR -- bu nedenle ERISILEMEYEN (unreachable) bir PANIC durumu.
* src/query.rs -- TUM sorgu-parametreleri `urlencoding::encode` ILE DOGRU sekilde KODLANIYOR -- injection riski YOK; bu dosya SADECE YEREL ARGUMAN-AYRISTIRMA/JSON-OLUSTURMA MANTIGI ICERIYOR, saldirgan-erisilebilir bir YUZEY DEGIL (TUM girdi, KULLANICININ KENDI KOMUT-SATIRI ARGUMANLARI).
* SONUC: Bu, bu oturumda incelenen Brave hedefleri arasinda EN YUKSEK kod-KALITESINE/guvenlik-BILINCINE sahip KUTUPHANELERDEN biri -- her DOSYADA acik YORUMLARLA GEREKCELENDIRILMIS DEFANSIF tasarim KARARLARI (redirect-devre-disi, boyut-sinirlari, atomik dosya YAZMA, UTF-8 SINIR-guvenligi). Odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI, rapor TEMIZ olarak dispatch edilmeli.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._