# Bug Bounty Raporu — brave_brave-core-crx-packager

**Tarih:** 2026-11-05 08:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/brave-core-crx-packager (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_brave-core-crx-packager/raw`
* **Engellenen/erişilemeyen adımlar:** Repo COK BUYUK (~45 dosya) VE ZAMAN KISITI nedeniyle TUM paketleme scriptleri (orn. scripts/packageAdBlock.js, scripts/generatePuffpatches.js, scripts/generateNTPBackgroundImages.js, scripts/packageP3AConfig.js VE digerleri) satir-SATIR incelenemedi -- INCELEME, EN YUKSEK-DEGERLI dosyalara (imzalama/CRX-paketleme CEKIRDEGI, S3/GitHub-release FETCH+DOGRULAMA boru-hatlari, zip-slip SAVUNMALARI) ODAKLANDI. scripts/uploadComponent.js VE dataFilesWebMcp.js/dataFilesBravePsst.js TAM detayli incelenmedi.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] scripts/packageTorClient.js'teki SHA512 hash GUNCELLEMESI VE scripts/ntp-sponsored-images/params.js'teki region-filtresi FAIL-CLOSED duzeltmesi (iki commit diff'i) -- bunlar ZATEN YAPILMIS, iyi-yonlu GUVENLIK/HIJYEN duzeltmeleri, BAGIMSIZ bir bulgu DEGIL (tersine, bu teslimin KENDISININ aktif-olarak SAGLAMLASTIRILDIGINI GOSTERIYOR).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave tarayicisina dagitilan TUM bilesen-GUNCELLEMELERINI (adblock listeleri, NTP sponsorlu GORSELLER, cuzdan VERI dosyalari, Tor istemcisi, yerel AI MODELLERI VB.) imzalayip CRX FORMATINDA PAKETLEYEN merkezi altyapi -- bu nedenle TEDARIK-ZINCIRI acisindan EN KRITIK hedeflerden biri, critical severity ile TUTARLI.
* `lib/crx.js`/`lib/crx3.pb.js`/`lib/contentSign.js` -- CRX3 imzalama FORMATI (magic header, RSA-SHA256 SignedData imzasi, treehash-tabanli verified_contents.json) STANDART SPESIFIKASYONA uygun SEKILDE DOGRU UYGULANMIS; kriptografik zayiflik VEYA format-KARISIKLIGI BULUNAMADI.
* `lib/walletLists.js::fetchWalletLists()` -- brave/wallet-lists GitHub RELEASE'inden indirme: `gh release verify-asset` + `gh attestation verify` (SLSA build PROVENANCE, `--source-ref refs/heads/main`, `--deny-self-hosted-runners`) ILE KRIPTOGRAFIK SAGLAMA, SONRA `extractZip()`'in `ntpUtil.validateTargetPath()` ILE DOGRU UYGULANMIS bir zip-slip SAVUNMASINDAN GECIYOR -- OLAGANUSTU iyi SAVUNULMUS bir TEDARIK-ZINCIRI dogrulama ZINCIRI.
* `lib/ntpUtil.js::validateTargetPath()` -- `path.resolve()` + trailing-separator EKLEYEREK sibling-prefix KACISINI (orn. `<root>-evil`) ENGELLEYEN DOGRU bir path-traversal SAVUNMASI, `prepareAssets()` TARAFINDAN DOGRU SEKILDE HER indirilen VARLIK icin KULLANILIYOR, AYRICA her VARLIGIN SHA256 hash'i BEKLENEN degerle KARSILASTIRILIYOR.
* `lib/util.js::s3capableFetch()` -- S3 indirmeleri icin `permittedBuckets` SABIT-ALLOWLIST'I ILE EK bir SAVUNMA katmani (KENDI YORUMUNDA da belirttigi gibi, IAM izinlerinin YETERLI OLMASI gerekse de DEFENSE-IN-DEPTH olarak EKLENMIS).
* `lib/adBlockRustUtils.js` -- TUM fetch() cagrilari SABIT, HARDCODED `raw.githubusercontent.com/brave/adblock-resources/...` URL'lerine, DIS/degiskeni URL-insasi YOK.
* `lib/localModelsDownloader.js` -- `brave/leo-local-models.git`'ten `git clone`+sparse-checkout (execSync STRING-interpolasyonlu AMA `sparseCheckoutPath`/`repoUrl` parametreleri HER ZAMAN cagiran SCRIPT'LERDEN (generateLeoLocalModelsDataFiles.js VB.) SABIT, HARDCODED degerlerle GELIYOR, dis/saldirgan girdisi YOK) -- KUCUK bir hijyen NOTU: belirli bir COMMIT SHA'sina PINLENMEMIS (SADECE `--depth 1` ile EN SON main), AMA bu Brave'in KENDI DEPOSU, DIS bir GUVEN SINIRINI GECMIYOR.
* `lib/util.js::generateCRXFile()`/`ntpUtil.js::generatePublicKeyAndID()` -- STRING-interpolasyonlu `execSync` KULLANIMI (shell-yorumlanan) GORULUYOR, AMA incelenen TUM CAGRI-NOKTALARINDA parametreler (binary yolu, anahtar dosyasi yolu, inputDir) HER ZAMAN Jenkins-TARAFINDAN SAGLANAN, operator-KONTROLLU CLI argumanlari/SABIT build-DIZINLERI -- dis saldirgan-kontrollu bir deger akisi BULUNAMADI.
* SONUC: Incelenen EN YUKSEK-ONCELIKLI dosyalarda (imzalama, CRX paketleme, wallet-lists/NTP varlik FETCH+DOGRULAMA boru-hatlari, S3/adblock-kaynak indirme), odul-degeri TASIYAN YENI bir guvenlik bulgusu TESPIT EDILEMEDI -- kod TUTARLI olarak dikkatli, DEFENSE-IN-DEPTH SAVUNMALAR iceriyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._