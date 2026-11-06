# Bug Bounty Raporu — brave_star-randsrv

**Tarih:** 2026-11-06 02:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/star-randsrv (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Rust. Description: Go wrapper service for the STAR randomness server.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_star-randsrv/raw`
* **Engellenen/erişilemeyen adımlar:** Gercek dagitim topolojisi (bu servisin bir AWS Nitro Enclave icinde calistigini VE enclave-ile-parent-instance arasindaki vsock-proxy katmaninin (bu repo'nun DISINDA, genellikle ayri bir proxy bileseni) herhangi bir hiz-sinirlama/baglanti-sinirlama uyguluyor OLUP OLMADIGINI) bu teslimin KAPSAMI DISINDA -- bu nedenle F1'in GERCEK dunya CIDDIYETI (operasyonel bir hiz-sinirlayici katmanin VAR OLUP OLMADIGI) KESIN olarak DOGRULANAMADI., `sta-rs`/`ppoprf` kutuphanesinin KENDI ic KAYNAK KODU (bu teslimde YOK, sadece bir DIS bagimlilik olarak REFERANS EDILIYOR) incelenemedi -- `state.server.eval()` cagrisinin GERCEK hesaplama MALIYETI (EC scalar carpim SAYISI/karmasikligi) TAHMIN EDILDI (standart OPRF/Ristretto islemleri icin TIPIK), KESIN olarak OLCULMEDI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i (Cargo bagimlilik/lint GUNCELLEMELERI gibi gorunen kucuk degisiklikler) -- kod DAVRANISINI ETKILEMEYEN DEGISIKLIKLER, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, STAR (Secret-sharing-based Threshold Aggregation Reporting) GIZLILIK-korumali TELEMETRI protokolu icin kullanilan, Rust-tabanli bir OPRF (Oblivious Pseudorandom Function) 'randomness sunucusu' -- Brave tarayicisinin KENDISI TARAFINDAN kullanilan, YUKSEK-guven GEREKTIREN bir kriptografik bilesen, AWS Nitro Enclave icinde CALISTIRILMASI tasarlanmis (remote attestation ile).
* src/state.rs::epoch_loop -- epoch-ROTASYON VE 'puncture' (anahtar-delme/FORWARD-gizlilik) mekanizmasini SATIR SATIR inceledim: ESKI epoch HER ZAMAN yeni epoch'a GECMEDEN ONCE punctured (delindi) -- BU, GECMIS epoch'lar icin DEGERLENDIRME uretmenin ARTIK IMKANSIZ OLDUGUNU GARANTI EDIYOR (STAR'in forward-gizlilik GARANTISI). Puncture BASARISIZ olursa KOD KASITLI olarak PANIC ediyor (availability'YI GIZLILIK UGRUNA FEDA EDIYOR) -- bu, bu TUR bir kriptografik servis icin DOGRU tasarim KARARIDIR.
* src/handler.rs::randomness -- `request.epoch` istemci-TARAFINDAN BELIRTILEBILIR (opsiyonel alan), ANCAK sunucu SADECE kendi GUNCEL (`state.epoch`) ile TAM ESLESIRSE KABUL EDIYOR (`if epoch != state.epoch { return Err(Error::BadEpoch(epoch)); }`) -- bu, ESKI (punctured) bir epoch'u ZORLA TALEP ETME GIRISIMINI ENGELLIYOR; GERCEKTEN eskimis bir epoch TALEP EDILDIGINDE, PPOPRF KUTUPHANESININ KENDISI de (punctured anahtar NEDENIYLE) BASARISIZ OLURDU -- IKI KATMANLI bir SAVUNMA.
* src/util.rs, src/main.rs::Config -- CLI argumanlari (instance-name, epoch-duration VB.) SADECE SUNUCU BASLATICISI TARAFINDAN KONTROL EDILIYOR (saldirgan-ERISILEBILIR bir girdi DEGIL) -- injection/manipulation riski YOK.
* SONUC: Bu oturumda TEK bir bulgu (F1) var -- `/randomness` endpoint'inde kimlik-dogrulama/hiz-sinirlama/esZAMANLILIK KISITLAMASININ TAMAMEN EKSIK OLMASI, MAX_POINTS=1024 ile BIRLESTIGINDE, kimlik-dogrulamasiz, hesaplama-maliyeti-ASIMETRIK bir DoS vektoru OLUSTURUYOR. Protokolun KENDISININ kriptografik GIZLILIK garantileri (epoch-puncturing) SAGLAM VE DOGRU uygulanmis durumda.

## 📊 Bulgu F1: /randomness (VE /instances/:instance/randomness) endpoint'inde HICBIR kimlik-dogrulama, hiz-sinirlama (rate limiting) VEYA esZAMANLILIK SINIRI YOK -- MAX_POINTS=1024 ile BIRLESINCE, hesaplama-maliyeti ASIMETRIK, kimlik-dogrulamasiz uzaktan DoS
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-770 (Allocation of Resources Without Limits or Throttling) / CWE-400 (Uncontrolled Resource Consumption)
* **Stage 2 Confidence:** 32/100 — Stage1'in 'hicbir rate-limit/concurrency-limit/auth katmani YOK' iddiasini BAGIMSIZ olarak YENIDEN DOGRULADIM: `src/main.rs::app()` icindeki axum Router ZINCIRINI satir-satir OKUDUM -- SADECE `.layer(tower_http::trace::TraceLayer::new_for_http())` VAR, baska HICBIR middleware/layer EKLENMEMIS. Ham veri DUMP'inin TAMAMINDA `rate`, `governor`, `throttl`, `Semaphore`, `ConcurrencyLimit`, `body_limit` desenleri icin AYRICA grep YAPTIM -- SIFIR ESLESME, bu stage1'in BULGUSUNU DOGRULUYOR.

BU BULGUYU CURUTMEYE CALISTIM: (1) Belki `MAX_POINTS=1024` sinirinin KENDISI YETERLI bir KORUMADIR? HAYIR -- bu SADECE TEK bir isteğin boyutunu SINIRLIYOR, BIRIM-zamanda KAC istek GONDERILEBILECEGINI SINIRLAMIYOR; bir saldirgan HALA 1024-noktali istekleri PARALEL/TEKRARLANAN olarak gonderebilir. (2) Belki `state.server.eval()` ACTUALLY COK UCUZ bir islemdir VE 'asimetrik-maliyet' iddiasi ABARTILI? Bu teslimde `ppoprf` KUTUPHANESININ KENDI KAYNAGI YOK, bu nedenle KESIN bir MALIYET-OLCUMU yapamadim -- ANCAK Ristretto/OPRF degerlendirmesi STANDART olarak eliptik-egri skaler-carpim(lar) GEREKTIRIR, bu HTTP-echo'dan DOGAL olarak DAHA PAHALI bir ISLEMDIR; bu VARSAYIM mantikli AMA KESIN-OLCULMEMIS. (3) Belki GERCEK dagitim (AWS Nitro Enclave + vsock-proxy, veya onunde bir LOAD BALANCER/WAF) ZATEN HARICI bir hiz-sinirlama SAGLIYOR? Bu TAMAMEN MUMKUN VE bu teslimin KAPSAMI DISINDA -- bu NEDENLE bulgunun NIHAI GERCEK-DUNYA CIDDIYETI DOGRULANAMAZ.

STAGE1'IN kriptografik-GIZLILIK DEGERLENDIRMESINI (epoch-puncturing, BadEpoch REDDI) BAGIMSIZ olarak KOD-TAKIBIYLE DOGRULADIM -- bu KISIM SAGLAM, F1 ILE ILGISIZ VE DOGRU uygulanmis. F1'in KENDISI GECERLI bir kod-SEVIYESI EKSIKLIK (bu, COK PROGRAMDA 'basit/genel DoS' KATEGORISINDE DUSUK-ONCELIKLI/kapsam-DISI olarak ELE ALINAN bir SINIF, ozellikle amplifikasyon FAKTORU KESIN olarak OLCULEMEDIGI icin) -- bu nedenle confidence'i DUSUK-ORTA (32) DUZEYDE SABITLEDIM: kod-EKSIKLIGI KESIN VE BAGIMSIZ dogrulandi, ANCAK bu, bu oturumda incelenen DAHA KESIN/SOMUT mantik-hatalarindan (orn. adblock-rust F1, brave-search-mcp-server F1) DAHA ZAYIF bir bulgu -- cunku (a) amplifikasyon-maliyeti TAHMIN, KESIN-OLCUM DEGIL VE (b) dagitim-topolojisi (Nitro enclave onu/ARKASI) bilinmiyor.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._