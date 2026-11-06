# Bug Bounty Raporu — brave_go-translate

**Tarih:** 2026-11-06 18:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/go-translate (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Go. Description: Translation adapter / relay server for Brave.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_go-translate/raw`
* **Engellenen/erişilemeyen adımlar:** `middleware.BearerToken` (github.com/brave-intl/bat-go/libs/middleware) `server/server.go::setupRouter()`'da TUM route'lara (`/translate_a/t`, `/translate_a/l`, VE statik varlik-sunan `/static/v1/*`) UYGULANAN kimlik-dogrulama MIDDLEWARE'I -- bu paketin KENDI KAYNAK KODU bu teslimde YER ALMIYOR (DIS bagimlilik). Bu nedenle, `/translate_a/t`'nin GERCEKTEN kimlik-dogrulamasiz/HARICI saldirganlar tarafindan ERISILEBILIR OLUP OLMADIGI (sabit bir ON-PAYLASIMLI gizli anahtar mi gerektiriyor, yoksa anonim/salt-okunur istekler icin bir ISTISNA mi var) KESIN olarak DOGRULANAMADI -- F1'in GERCEK-dunya erisilebilirligi bu BELIRSIZLIGE BAGLI., `load_scripts.py` (assets/element.js'i olusturan BUILD-zamani script) VE `assets/static/v1/element.js`'in TAM mantigi (6000+ satir, muhtemelen upstream Google Translate Element'in DEGISTIRILMIS bir KOPYASI) ZAMAN KISITI nedeniyle SATIR-SATIR incelenemedi -- SADECE route-KAYDI/baslik-KONFIGURASYONU (CSP/CORS) seviyesinde gozden GECIRILDI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i -- gorunuse gore kucuk BAGIMLILIK/konfigurasyon GUNCELLEMELERI, kod-MANTIGI DEGISIKLIGI DEGIL, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave tarayicisinin SAYFA-ICI ceviri OZELLIGI icin Google-formatindaki istekleri Lingvanex-formatina CEVIREN bir Go RELAY/ADAPTOR sunucusu.
* translate/translate.go::GetLanguageParams/ToLingvanexRequest -- `sl`/`tl` dil KODLARI, language.go'daki SABIT, Chromium-TURETILMIS bir ALLOWLIST'E (`ToLnxLanguageCode`) KARSI DOGRULANIYOR -- GECERSIZ/rastgele bir dil kodu DIREKT REDDEDILIYOR (400), injection/path-manipulasyon riski YOK.
* controller.go::LnxEndpointConfiguration::GetEndpoint -- bilinmeyen bir (from,to) CIFTI icin AGIRLIK haritasi BOS OLSA bile, DONGU GUVENLI bir sekilde `c.Endpoints[0]`'A (operator-YAPILANDIRMASI, saldirgan-kontrollu DEGIL) DUSUYOR -- SSRF/yonlendirme RISKI YOK, endpoint HER ZAMAN sabit/operator-tanimli `LNX_HOST` listesinden GELIYOR.
* controller.go::ServeStaticFile -- GUVENLI CSP/CORS/X-Frame-Options BASLIKLARI DOGRU AYARLANMIS; `http.FileServer` SADECE `assets/` ALT-dizinine BAGLI (path traversal, standart Go `http.Dir` davranisi nedeniyle SINIRLI).
* SONUC: Bu oturumda TEK bir bulgu (F1) var -- yukarı-akis backend YANITININ Content-Type BASLIGINA KOSULSUZ indeksleme, backend bu BASLIGI ATLARSA tek-istek SEVIYESINDE bir panic/DoS'a yol ACIYOR. Erisilebilirligi, teslim KAPSAMI DISINDAKI bir auth-middleware'e BAGLI oldugundan DUSUK confidence ONERILIYOR.

## 📊 Bulgu F1: controller.Translate(): yukarı akis (Lingvanex) yanıtının Content-Type başlığına, boş-dizi kontrolü olmadan koşulsuz indeksleme (`[0]`) -- backend yanıtı bu başlığı atlarsa panic/DoS
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-20 (Improper Input Validation) / CWE-248 (Uncaught Exception) -- DoS
* **Stage 2 Confidence:** 22/100 — Stage1'in `lnxResp.Header["Content-Type"][0]`'in KOSULSUZ VE boş-kontrolsuz INDEKSLEME oldugunu BAGIMSIZ olarak dogruladim -- Go'nun `http.Header` tipinin (`map[string][]string`) EKSIK bir anahtar icin `nil` slice DONDURDUGUNU VE `nil[0]`'in bir panic URETTIGINI (standart Go DAVRANISI) TEYIT ETTIM; satirin GERCEKTEN `StatusCode` kontrolunden ONCE CALISTIGINI da satir-NUMARALARINI TAKIP EDEREK dogruladim. `controller_test.go`'da `Translate()` fonksiyonu icin SIFIR test KAPSAMI OLDUGUNU da BAGIMSIZ olarak dogruladim (SADECE GetEndpoint/NewLnxEndpointConfiguration test EDILIYOR).

BU BULGUYU CURUTMEYE CALISTIM VE IKI ONEMLI SINIRLAMA BULDUM: (1) `server/server.go::setupRouter()`'da `middleware.BearerToken` TUM route'lara (TRANSLATE DAHIL) UYGULANIYOR -- bu paketin KAYNAGI bu teslimde YOK, bu nedenle bu endpoint'in GERCEKTEN kimlik-dogrulamasiz/HARICI saldirganlara ACIK OLUP OLMADIGI BILINMIYOR; eger sabit bir PAYLASILAN SIR gerektiriyorsa, F1 SADECE ZATEN GECERLI bir token'a sahip bir TARAF (orn. Brave'in KENDI altyapisi) icin GECERLI OLUR, DIS bir saldirgan icin DEGIL. (2) Go'nun net/http sunucusu VARSAYILAN olarak TEK bir handler'daki panigi O BAGLANTI icin KURTARIR -- bu nedenle ETKI TAM servis-COKMESI DEGIL, SADECE o TEK istegin TEMIZ olmayan bir sekilde BASARISIZ OLMASI (baglanti KOPMASI). AYRICA, bu KOSULUN TETIKLENMESI icin saldirganin Lingvanex BACKEND'INI Content-Type'SIZ bir YANIT VERMEYE ZORLAMASI GEREKIYOR -- bu, backend'in KENDI (bu teslimde YER ALMAYAN) DAVRANISINA BAGLI, DOGRUDAN saldirgan-KONTROLLU bir ETMEN DEGIL.

Bu UC BELIRSIZLIK (auth-gereksinimi, panic-kapsam-sinirlamasi, backend-DAVRANISINA baglilik) BIRLESINCE, bu bulguyu bu oturumda incelenen DIGER PASS bulgularindan (orn. sta-rs F1, brave-search-mcp-server F1 -- HER IKISI de dogrudan, KOSULSUZ saldirgan-eriSEBILIR) ACIKCA DAHA ZAYIF kiliyor. Kod-SEVIYESI defekt KESIN VE GERCEK (eksik boş-kontrol), ANCAK GERCEK-dunya istismar EDILEBILIRLIGI COK sayida bilinmeyen FAKTORE bagli oldugundan confidence'i DUSUK (22) SABITLEDIM -- Zero-False-Positive ilkesi geregince bu, 'teorik olarak ENDISE verici ANCAK pratik istismar-edilebilirligi BELIRSIZ' kategorisine YAKIN, ama TAMAMEN REDDEDILECEK kadar ZAYIF DEGIL CUNKU kod defekti kendisi TARTISMASIZ VE test-KAPSAMI SIFIR.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._