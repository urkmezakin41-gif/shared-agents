# Bug Bounty Raporu — brave_sta-rs

**Tarih:** 2026-11-06 17:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/sta-rs (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Rust. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_sta-rs/raw`
* **Engellenen/erişilemeyen adımlar:** KALICI (permanent) static-analysis-only kisitlama GEREGINCE: `ppoprf/src/ggm.rs` (GGM-agaci tabanli delinebilir PRF) VE `adss/src/lib.rs` (Adept Secret Sharing semasi) GIBI DERIN kriptografik PROTOKOL mantigi, YURUTULEBILIR bir PoC/exploit OLUSTURMADAN, SADECE elle kod-OKUMA ile DEGERLENDIRILDI -- bu, bu TUR bir delinebilir-PRF agacinin DOGRULUGUNU KESIN olarak KANITLAMAK icin YETERLI DERINLIKTE bir KRIPTOGRAFIK protokol-ANALIZI SAGLAMAZ (bu, bu oturumun KAPSAMI VE YONTEMI DISINDADIR). Mevcut TEST paketinin (puncture_eval_consistent, multiple_puncture, puncture_all VB.) GENIS-KAPSAMLI OLDUGU GOZLEMLENDI, bu da BU KATMANDA ACIK bir MANTIK hatasi OLASILIGINI DUSURUYOR., `star/src/lib.rs`'in TAMAMI (3800+ satir, MessageGenerator/share_recover protokol MANTIGI) ZAMAN KISITI nedeniyle SATIR-SATIR incelenemedi -- SADECE F1 ile ILGILI bolum (Share::from_bytes, star-wasm baglanti NOKTASI) VE panik/unwrap DESENLERI icin HEDEFLI bir TARAMA yapildi.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i (bagimlilik/lint GUNCELLEMELERI gibi gorunen kucuk degisiklikler) -- kod DAVRANISINI ETKILEMEYEN, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, STAR (Secret-sharing-based Threshold Aggregation Reporting) protokolunun CEKIRDEK kriptografik KUTUPHANE IMPLEMENTASYONU -- `ppoprf` (star-randsrv'nin DAYANDIGI OPRF), `sharks`/`adss` (Shamir SECRET sharing VE Adept Secret Sharing), `star` (ustteki istemci-TARAFI protokol MANTIGI) VE `star-wasm` (tarayici/Node.js icin WASM BAGLANTILARI) ICERIYOR. README'de 'denetlenmemis, KENDI RISKINIZLE kullanin' UYARISI MEVCUT.
* ppoprf/src/ppoprf.rs::Server::eval/puncture -- star-randsrv'DE GOZLENEN epoch-puncturing DAVRANISININ TEMELINI OLUSTURAN KOD BURADA -- `GGM::puncture`'in COK SAYIDA test ile (puncture_eval_consistent, multiple_puncture, puncture_all) KAPSANDIGI GOZLEMLENDI; DLEQ-proof dogrulama MANTIGI (ProofDLEQ::new_batch/verify_batch) standart VOPRF taslaginin YAPISINI TAKIP EDIYOR GIBI GORUNUYOR (TAM kriptografik dogrulama bu oturumun KAPSAMI DISINDA).
* sharks/src/share_ff.rs::Share::try_from -- BU KATMANDA (TryFrom<&[u8]>) Share AYRISTIRMA KODU DOGRU VE GUVENLI: once UZUNLUK KONTROLU YAPILIYOR, SONRA ICERIDEKI `.expect()` cagrilari BU KONTROL SAYESINDE HICBIR ZAMAN BASARISIZ OLAMAYACAK SEKILDE KORUNUYOR (ARTIK-tehlikesiz), VE GECERSIZ alan-TEMSILLERI (field representation >= modulus) `Option`/`Result` ARACILIGIYLA DUZGUN REDDEDILIYOR -- bu KATMANIN KENDISI GUVENLI; F1'in KOK-NEDENI SADECE star-wasm BAGLANTI-NOKTASINDAKI KORUMASIZ `.unwrap()` CAGRILARIDIR, ALTTAKI KUTUPHANE KATMANLARI DEGIL.
* SONUC: Bu oturumda TEK, SOMUT olarak DOGRULANMIS bir bulgu (F1) var -- star-wasm'in `group_shares()` fonksiyonundaki EKSIK hata-YONETIMI, aggregation SIRASINDA tek bir kotu-bicimlendirilmis istemci-payından (share) KAYNAKLANAN bir DoS'a yol ACIYOR.

## 📊 Bulgu F1: star-wasm::group_shares(): COKLU, FARKLI istemcilerden GELEN paylasimlari (shares) ISLERKEN, SADECE BIRI bozuk/gecersiz OLSA bile TUM gruplamayi PANIKLE COKERTEN iki korumasiz `.unwrap()` cagrisi -- kimlik-dogrulamasiz uzaktan DoS
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-248 (Uncaught Exception) / CWE-20 (Improper Input Validation) -- DoS
* **Stage 2 Confidence:** 44/100 — Stage1'in IDDIASINI BAGIMSIZ olarak SATIR SATIR YENIDEN DOGRULADIM: `star-wasm/src/lib.rs::group_shares()`'in `Share::from_bytes(&BASE64_STANDARD.decode(chunk).unwrap()).unwrap()` SATIRINI, ALTINDAKI TUM KATMANLARI (`star/src/lib.rs::Share::from_bytes` -> `InternalShare::from_bytes(bytes)?` -> adss KATMANI, `sharks/src/share_ff.rs::Share::try_from`) TAKIP EDEREK dogruladim -- TUM ALT-katmanlar GERCEKTEN `Option`/`Result` DONDURUYOR (PANIKLEMIYOR), bu nedenle `group_shares`'DEKI CIFT `.unwrap()` GERCEKTEN TEK HATA-YONETIMI NOKTASI VE GERCEKTEN KORUMASIZ. AYNI DOSYADAKI KARDES fonksiyon `create_share()`'in AYNI TUR bir HATAYI (`share_result.is_err()`) DUZGUN KONTROL ETTIGINI DOGRULADIM -- bu, `group_shares`'in EKSIK hata-yonetiminin bir TASARIM KARARI DEGIL, bir GOZDEN KACIRMA OLDUGUNU GOSTERIYOR.

STAGE1'IN 'WASM INSTANCE'I KALICI olarak ZEHIRLEYEBILIR' seklindeki DAHA GUCLU iddiasini SORGULADIM: `star-wasm/src/lib.rs`'in TAMAMINI yeniden OKUDUM -- modulde HICBIR KALICI/GLOBAL mutable STATE (static degisken) YOK, HER iki `#[wasm_bindgen]` fonksiyonu (`create_share`, `group_shares`) TAMAMEN SAF/stateless. Bu nedenle bir panigin, modulun KENDISINI (BASKA cagrilari da ETKILEYECEK SEKILDE) KALICI olarak BOZMASI daha AZ OLASI -- tipik `wasm_bindgen` DAVRANISINDA bu, SADECE o TEK cagriyi bir JS exception'A CEVIRIR. STAGE1'IN bu KISMINI 'olabilir' seklinde YUMUSATILMIS bulduğum icin DUZELTME GEREKTIRMIYOR (zaten KOŞULLU ifade EDILMIS), ANCAK confidence'imi BU BELIRSIZLIGI YANSITACAK sekilde AYARLADIM.

ASIL cekirdek iddia (TEK bir kotu-bicimlendirilmis share'in, FONKSIYONUN KENDI IMZASININ VAAT ETTIGI `Option<String>` DONUS-DEGERI YERINE bir PANIC/exception URETMESI, bu da CAGIRANIN -- aggregation SUNUCUSUNUN -- bu durumu BEKLEMEDIGI/yakalamadigi bir HATA sinifi OLUSTURMASI) GECERLI VE BAGIMSIZ olarak dogrulandi. Bu, bu oturumda incelenen DIGER 'eksik hata-yonetimi/kaynak-temizleme' bulgularina (brave-search-mcp-server'in transports-Map sizintisi) BENZER bir OLGUNLUK seviyesinde -- kod-SEVIYESI defekt KESIN, ETKI availability-SINIRLI (DoS), GERCEK-dunya CIDDIYETI (batch-DUZEYINDE mi yoksa DAHA KALICI mi) TAM OLARAK bilinmiyor. confidence 44 olarak SABITLEDIM.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._