# Bug Bounty Raporu — brave_brave-search-mcp-server

**Tarih:** 2026-11-06 01:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/brave-search-mcp-server (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_brave-search-mcp-server/raw`
* **Engellenen/erişilemeyen adımlar:** `src/testUtils/mcpTestHarness.ts` ve tum `*.test.ts`/`*.spec.ts` dosyalari (teslimde sadece kaynak dosyalar var, test dosyalari INCLUDE edilmemis) incelenemedi -- bu nedenle `transports` Map'inin test-KAPSAMININ (coverage) bu davranisi zaten BEKLENEN/bilinen bir sinirlama olarak ele ALIP ALMADIGI DOGRULANAMADI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki bagimlilik-guncelleme commit diff'i (package-lock.json: @modelcontextprotocol/sdk 1.30.0->^1.32.2, zod 4.3.6->^4.6.7, body-parser vb. transitive guncellemeler) -- rutin bagimlilik bakimi, kod DEGISIKLIGI yok, guvenlik acisindan NOTR/pozitif.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Search API'sini Model Context Protocol (MCP) uzerinden bir LLM'e SUNAN resmi TypeScript sunucusu -- STDIO (varsayilan, Claude Desktop GIBI yerel istemciler icin) VE HTTP (uzak/paylasimli dagitim icin) transport'larini DESTEKLIYOR.
* src/protocols/rebinding.ts::createDnsRebindingGuard -- BU KOD TABANININ EN KRITIK YENI guvenlik YUZEYI (MCP'ye OZGU DNS-rebinding saldiri SINIFINA karsi KORUMA) SATIR SATIR incelendi VE DOGRU bulundu: Origin HER ZAMAN dogrulaniyor (loopback VEYA acik allowlist), Host SADECE allowedHosts yapilandirildiginda (opt-in) dogrulaniyor -- bu, resmi MCP ekosisteminin (2025 DNS-rebinding CVE'lerinden SONRA) ONERDIGI TAM olarak DOGRU desen. `isLoopbackHostname()` (utils.ts) TAM-ESLESME (exact-match) kontrolu kullaniyor ('localhost', '::1', VEYA gecerli 127.0.0.0/8) -- 'localhost.evil.com' GIBI alt-dize/substring BYPASS'I YOK, oncu-sifir (leading-zero) OCTAL-kaçirma TRIGI de REDDEDILIYOR. Varsayilan `host` degeri `127.0.0.1` (guvenli) -- `0.0.0.0`'a BAGLAMA SADECE acik bir dagitim/konfigurasyon SECIMI, kod DEFEKTI DEGIL.
* src/BraveAPI/index.ts::issueRequest -- TUM HTTP istekleri SABIT `https://api.search.brave.com` tabanina GIDIYOR, saldirgan-KONTROLLU hicbir HOST/path YOK -- SSRF riski YOK. `goggles` parametresi (keyfi HTTPS URL'leri KABUL ediyor) SADECE Brave'in KENDI arama API'SINE bir SORGU-PARAMETRESI olarak ILETILIYOR (bu MCP sunucusu TARAFINDAN SUNUCU-tarafinda hic FETCH EDILMIYOR) -- bu nedenle bu da SSRF DEGIL.
* src/jsonSchemaDialect.ts -- SADECE JSON Schema dialect UYUMLULUK duzeltmesi (SDK'nin draft-07 ciktisini 2020-12'ye YENIDEN-hedefleme), guvenlik-ilgili HICBIR mantik ICERMIYOR, prototype-pollution riski YOK (dogrudan KULLANICI JSON'u PARSE etmiyor, sadece ONCEDEN-tanimli Zod semalarini SERIALIZE ediyor).
* SONUC: Bu oturumda TEK, SOMUT olarak DOGRULANMIS bir bulgu (F1) var -- HTTP transport modundaki `transports` oturum-Map'inin SINIRSIZ/sonsuz BUYUMESI (eksik oturum-temizleme), kimlik-dogrulamasiz UZAKTAN tetiklenebilir bir kaynak-tukenmesi (bellek) DoS'u OLUSTURUYOR.

## 📊 Bulgu F1: HTTP transport (StreamableHTTPServerTransport) oturum Map'i (`transports`) hicbir zaman temizlenmiyor -- her yeni MCP oturumu SONSUZA KADAR bellekte tutuluyor, kaynak-tukenmesi (bellek sizintisi) tabanli Denial-of-Service
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-401 (Missing Release of Memory after Effective Lifetime) / CWE-400 (Uncontrolled Resource Consumption)
* **Stage 2 Confidence:** 48/100 — Stage1'in IDDIASINI BAGIMSIZ olarak YENIDEN DOGRULADIM: ham veri DUMP'inin TAMAMINDA (tum commit diff'leri + tum FULL FILE icerikleri) `onclose` dizesini ARADIM -- SIFIR ESLESME (grep exit code 1). Bu, `StreamableHTTPServerTransport` ORNEGINE HICBIR YERDE bir `.onclose` CALLBACK'I ATANMADIGINI KESIN olarak DOGRULUYOR -- resmi MCP SDK referans SUNUCULARININ (orn. typescript-sdk ornekleri) STANDART olarak KULLANDIGI 'transport.onclose = () => delete transports[sid]' DESENI bu dosyada TAMAMEN YOK. AYRICA `src/protocols/http.ts` dosyasini BASTAN SONA tekrar OKUYARAK, `transports` Map'ine SADECE `transports.set(...)` (satir ~1303) ile YAZILDIGINI, VE Map'TEN SILME/`delete`/temizleme islemi yapan HICBIR KOD YOLUNUN OLMADIGINI dogruladim -- `app.all('/mcp', ...)` TUM HTTP metodlarini (GET/POST/DELETE DAHIL) AYNI genel handler'a YONLENDIRIYOR VE transport.handleRequest()'e DELEGE EDIYOR, ANCAK bu cagridan SONRA (veya herhangi bir SDK-ic kapanma OLAYINDA) uygulama-SEVIYESI Map'ten SILME YAPAN BIR satir bile YOK.

STAGE1'IN ETKI-analizini SORGULADIM: 'initialize' istegi gercekten KIMLIK DOGRULAMASIZ MI? `getDefaultRequestHeaders()`/`config.braveApiKey` KULLANIMININ SADECE `BraveAPI/index.ts::issueRequest()` icinde (yani bir ARACIN (tool) GERCEKTEN cagrilmasi aninda) GERCEKLESTIGINI, session OLUSTURMA/`initialize` ASAMASINDA HICBIR Brave API anahtari veya BASKA bir dogrulama KONTROLU OLMADIGINI dogruladim -- bu nedenle 'initialize' istekleri GERCEKTEN kimlik-dogrulamasiz VE sadece DNS-rebinding Origin/Host kontrolunu GECMESI YETERLI (ki bu kontrol loopback dagitimlar icin OTOMATIK GECERLI, allowedOrigins yapilandirilmis WEB-tabanli dagitimlar icin ise HERHANGI bir izin-verilmis origin'den gelen ISTEK icin GECERLI).

KARSI-ARGUMAN olarak SUNU DEGERLENDIRDIM: belki gercek PRODUKSIYON dagitimi (orn. containerize edilmis, periyodik YENIDEN baslatma/scaling ile) bu sizintiyi OPERASYONEL olarak HAFIFLETIYOR -- ANCAK bu bir ALTYAPI/operasyon VARSAYIMI, kodun KENDISINDEKI defekti ORTADAN KALDIRMIYOR, VE README.md'nin HTTP modu 'surekli-calisan paylasimli sunucu' olarak ACIKCA BELGELEDIGI goz onune alindiginda, bu VARSAYIMIN HER dagitimda GECERLI OLACAGI GARANTI EDILEMEZ. Bu nedenle bulgu, STRUKTUREL bir kod defekti olarak GECERLI -- ANCAK NIHAI GERCEK-DUNYA ETKISI (ne kadar HIZLI OOM'a ULASILACAGI) dagitim OLCEGINE/kaynak-LIMITLERINE BAGLI OLDUGUNDAN, confidence'i orta-DUZEYDE (48) SABITLEDIM: mantik/kod-defekti KESIN VE BAGIMSIZ olarak dogrulandi, ETKISI kimlik-dogrulamasiz uzaktan DoS (bellek-guvenligi/veri-sizintisi DEGIL), ANCAK NIHAI patlama ZAMANI/ciddiyeti dagitim-olcegine BAGLI.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._