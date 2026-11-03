# Bug Bounty Raporu — base_ui

**Tarih:** 2026-11-03 04:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/ui (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_ui/raw`
* **Engellenen/erişilemeyen adımlar:** app/internal-explorer/flag.ts (EXPLORER_ENABLED tanimi), app/internal-explorer/chains.ts (resolveExplorerChain), app/internal-explorer/hosts.ts (originFromHostHeader) ve app/snapshots/r2.ts (getSnapshots) teslim edilmedi -- bu dosyalar Internal Explorer bolumunun build-zamani ayrilmasi ve host-header tabanli chain cozumlemesinin TAM detaylarini dogrulamak icin gerekli, ancak eldeki dosyalardan (guard.ts, chain.ts, config.ts, README.md) tasarimin nasil calistigi anlasilabiliyor.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Coinbase/Base'in Next.js (App Router) tabanli 'base/ui' uygulamasi -- Vercel'de yayinlanan genel-erisimli olcekleme/benchmark gosterge panelleri + yalnizca internal deployment'ta derlenen bir 'Internal Explorer' (blok/islem/bundle gozlemciligi) bolumu icerir.
* Son iki commit diff'i (b90ff628df, 424e92b20b) yalnizca /app/scaling altindaki kozmetik UI/metin degisiklikleri (etiket formati, gaz-limiti ikili-birim gosterimi) + eslesen testler -- guvenlik acisindan onemsiz.
* Internal Explorer bolumu (app/api/internal-explorer/*): her route handler'in basinda explorerDisabledResponse() cagriliyor -- EXPLORER_ENABLED false (public/Vercel build) ise 404 donuyor, boylece bolum 'sadece UI'da degil, derleme cikisindan tamamen' kaldiriliyor (kimlik bilgisi yoklugu nedeniyle 500 hatasi uzerinden sizinti riski de onlenmis). Bu, README'de de acikca belgelenmis kasitli bir tasarim (dahili dagitim vs public Vercel build ayrimi).
* RPC URL cozumlemesi (config.ts::getRpcUrl/getAuditRpcUrl) TAMAMEN sabit bir ortam-degiskeni haritasindan (TIPS_<CHAIN>_RPC_URL, chain ∈ {mainnet,sepolia,zeronet}) geliyor -- `?chain=` sorgu parametresi yalnizca bu sabit enum'dan birini SECMEK icin kullanilabiliyor, rpcUrl'in kendisi asla istemciden gelen bir deger degil. SSRF (Server-Side Request Forgery) icin somut bir yol BULUNAMADI.
* Audit RPC istemcisi (audit-events.ts) tum sorgulari parametreli JSON-RPC cagrilari (base_getTransactionEventsByHash/vb.) olarak yapiyor -- ham string concatenation veya SQL enjeksiyonuna acik bir yuzey yok (Postgres-backed olmasina ragmen sorgular RPC metod parametreleri uzerinden, serbest metin SQL uzerinden degil).
* block/[hash]/route.ts: 'identifier' hem blok numarasi hem hash olabilir -- isBlockNumber() /^\d+$/ regex'i ile ayristiriliyor, sayisal durumda BigInt() cagrisi guvenli (regex zaten rakamlarla sinirli); hash durumunda ham deger viem'in publicClient.getBlock({blockHash}) metoduna veriliyor (viem kendi dogrulamasini/JSON-RPC kodlamasini yapiyor, ham string RPC URL'ine enjekte edilmiyor).
* active-block.ts::parseActiveBlockQuery: 'before' sorgu parametresi /^(0|[1-9]\d*)$/ regex + Number.isSafeInteger kontrolu ile dogrulaniyor -- gecersiz/asiri buyuk deger InvalidBlockListQueryError ile reddediliyor.
* snapshots/route.ts: 'network' sorgu parametresi NETWORK_IDS.includes() ile sabit bir izin listesine (allowlist) karsi dogrulaniyor -- izin listesi disi deger 400 ile reddediliyor (path traversal/R2 anahtar enjeksiyonu icin somut bir yol bulunamadi, ancak r2.ts dosyasi teslim edilmedigi icin getSnapshots() icindeki R2 anahtar olusturma mantigi tam dogrulanamadi -- yukaridaki blocked_or_unreachable_steps'e bakiniz).
* Genel tarama: dangerouslySetInnerHTML, eval(), new Function(), child_process/execSync, dogrudan .innerHTML atamasi veya sabit kodlanmis sir/anahtar (API key/secret/token) ICIN tum teslim edilen dosyalar grep edildi -- hicbiri bulunamadi (yalnizca iki zararsiz redirect() cagrisi, ikisi de sabit path'lere).
* SONUC: Teslim edilen veri (trivial kozmetik commit diff'leri + genis bir statik TypeScript/Next.js kod tabani incelemesi) icinde PASS seviyesinde raporlanabilir bir guvenlik acigi TESPIT EDILEMEDI. Girdi dogrulamasi (regex + allowlist + sabit enum) tutarli ve dikkatli uygulanmis; RPC URL'leri hic bir noktada istemciden gelen veriden olusturulmuyor. Internal Explorer'in erisim kontrolu (EXPLORER_ENABLED disinda, VPN/ag-seviyesi kimlik dogrulamasi olup olmadigi) bu depodan gorunmuyor -- bu, bir güvenlik acigi degil, eksik bagimli dosya/altyapi-disi bir sinir; hint-tier olarak degil, sadece not olarak kayit ediliyor cunku somut, kanitlanabilir bir istismar yolu gosterilemiyor. Temiz rapor (findings=[]) teslim ediliyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._