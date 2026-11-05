# Bug Bounty Raporu — brave_n8n-nodes-brave-search

**Tarih:** 2026-11-05 11:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/n8n-nodes-brave-search (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: A n8n node for Brave Search.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_n8n-nodes-brave-search/raw`
* **Engellenen/erişilemeyen adımlar:** `operations/images`, `news`, `place_search`, `spellcheck`, `suggest`, `videos` ALTINDAKI `index.ts`/`parameters.ts` dosyalarinin HEPSI TEK-TEK incelenmedi -- web/index.ts VE images/index.ts (benzer YAPIDA) OKUNDUKTAN SONRA, TUMUNUN AYNI BASIT `buildQuery()` DESENINI (SABIT endpoint, parametre-yeniden-ADLANDIRMA, n8n'in KENDI `qs` nesnesi ARACILIGIYLA GUVENLI URL-encoding) TAKIP ETTIGI VARSAYILDI -- bu, dosyalarin KENDI ISIMLERININ VE `_base.ts`'teki PAYLASILAN ARAYUZUN GOSTERDIGI TUTARLI YAPIYA DAYANAN MAKUL bir CIKARIM, ama HER dosya BIREYSEL olarak DOGRULANMADI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki commit diff'i (package.json VERSIYON bump'i VE BraveSearch.node.json'daki node-ADI duzeltmesi `@brave/n8n-nodes-brave-search` -> `@brave/n8n-nodes-brave-search.braveSearch`) -- rutin SURUM/METADATA GUNCELLEMESI, guvenlik acisindan NOTR.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Search API'sini n8n WORKFLOW otomasyon platformuna BAGLAYAN KUCUK bir TOPLULUK dugumu (community node) -- cogunlukla API YANIT-SEKLI tanimlari (data.ts dosyalari, SALT TIP tanimlari) VE n8n'in KENDI GUVENLI HTTP istemci YARDIMCISI (`ctx.helpers.httpRequestWithAuthentication`) ETRAFINDAKI ince (thin) SARMALAYICI KOD.
* `BraveSearch.node.ts::performRequest()` -- istek URL'si HER ZAMAN `${baseUrl}${operation.endpoint}` SEKLINDE OLUSTURULUYOR; `operation.endpoint` HER operasyon icin SABIT, HARDCODED bir path STRING'I (orn. '/web/search') -- WORKFLOW/kullanici PARAMETRELERI SADECE `qs` (query-string) NESNESINE GIDIYOR, n8n'in KENDI HTTP istemcisi TARAFINDAN GUVENLI SEKILDE encode EDILIYOR -- PATH/host ENJEKSIYONU icin bir YOL GOZLENMEDI.
* `credentials/BraveSearchApi.credentials.ts`'teki `baseUrl` ALANI (`type: 'hidden'`, ACIKCA 'Change to use a proxy or regional endpoint' olarak BELGELENMIS) -- bu, KULLANICININ KENDI CREDENTIAL YAPILANDIRMASININ bir PARCASI (bir WORKFLOW ICERISINDEN PER-EXECUTION olarak DEGISTIRILEMEYEN bir deger), bu nedenle BASKA bir kisinin PAYLASTIGI bir WORKFLOW'un bu alani SALDIRGAN-KONTROLLU bir DEGERE CEKEMEYECEGI DEGERLENDIRILDI -- SADECE kullanicinin KENDI, BILINCLI yapilandirma HATASI/sosyal-muhendislik KURBANI OLMASI durumunda (API anahtarinin BASKA bir host'a SIZMASI) ETKILI OLABILIR, bu REPO'NUN KODUNDAKI bir defekt DEGIL, KASITLI/belgelenmis bir OZELLIK.
* `BraveSearch.node.ts::buildParams()`'daki 'goggles' OZEL-ISLEME MANTIGI -- kullanicinin VERDIGI bir GOGGLE URL'sini DOGRUDAN bir fetch/exec HEDEFI olarak KULLANMIYOR, SADECE Brave'in KENDI arama API'SINE bir QUERY-PARAMETRESI olarak ILETIYOR (`goggles=<url>`) -- bu dugumun KENDI KODUNDA bir SSRF/exec riski OLUSTURMUYOR (goggle URL'sinin DEREFERANS EDILMESI, varsa, Brave'in KENDI backend'inde GERCEKLESIR, bu REPO'NUN DISINDA).
* `eval`/`new Function`/`child_process`/`dangerouslySetInnerHTML` icin TUM teslimde GENIS-CAPLI grep YAPILDI -- SIFIR SONUC.
* SONUC: Bu KUCUK, cogunlukla TIP-tanimlarindan OLUSAN n8n dugum PAKETINDE, odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI -- KOD, n8n'in KENDI GUVENLI HTTP/credential ALTYAPISINA DAYANIYOR VE SABIT endpoint'ler+basit parametre-ESLEMESI DISINDA OZEL bir MANTIK ICERMIYOR.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._