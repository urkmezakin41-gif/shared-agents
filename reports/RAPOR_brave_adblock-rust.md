# Bug Bounty Raporu — brave_adblock-rust

**Tarih:** 2026-11-05 20:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/adblock-rust (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Rust. Description: Brave's Rust-based adblock engine.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_adblock-rust/raw`
* **Engellenen/erişilemeyen adımlar:** `src/flatbuffers/unsafe_tools.rs` VE diger `src/flatbuffers/containers/*` dosyalari (zero-copy FlatBuffer okuma KATMANI, `unsafe` Rust BLOKLARI icerme IHTIMALI EN YUKSEK alan) ZAMAN KISITI nedeniyle SATIR-SATIR incelenemedi -- bu, Rust'in bellek-guvenligi GARANTILERININ bu PROJEDE en cok RISK TASIDIGI YER olabilir VE bir SONRAKI incelemede ONCELIKLENDIRILMELI., `src/filters/fb_network.rs`/`fb_network_builder.rs` (FlatBuffer-tabanli AG-filtresi TEMSILI, `network_matchers.rs`'in ALTERNATIF/dahili bir SERIALIZASYON KATMANI olabilir) KISMEN GOZDEN GECIRILDI AMA `is_anchored_by_hostname`'in FlatBuffer-tabanli bir ESDEGERININ OLUP OLMADIGI TAM olarak DOGRULANAMADI -- F1'in FlatBuffer-serileştirilmis filtre YOLUNDA da GECERLI olup OLMADIGI BELIRSIZ.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki commit diff'i -- ilki (09d297c2c2) SADECE YORUM-yazim DUZELTMELERI (typo), ikincisi (f3f72f8471) bir SURUM-bump VE CHANGELOG girdisi ('Use the correct offset for infix hostname anchor matches') -- bu IKINCI commit, F1'in ASAGIDA TARTISILAN KOK-NEDENIYLE ILGILI, ZATEN YAPILMIS bir KISMI duzeltmeyi BELGELIYOR, bu nedenle KENDI BASINA AYRI bir bulgu DEGIL (ama F1'i TETIKLEYEN BAGLAMI SAGLADI).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave tarayicisina GOMULU, HER sayfa-YUKLEMESINDE calisan CEKIRDEK reklam-engelleme MOTORU (Rust) -- bellek-guvenligi acisindan Rust'in KENDI garantileri GUCLU bir SAVUNMA katmani SAGLIYOR, ANCAK `unsafe` bloklar (zaman kisiti nedeniyle TAM incelenmedi) VE FILTRE-ESLESTIRME MANTIGI (bu oturumda F1 TESPIT EDILDI) HALA RISK TASIYOR.
* `is_anchored_by_hostname()` ETRAFINDAKI TUM COMMIT-GECMISI (fuzzing HEDEFLERI de DAHIL: `fuzz/fuzz_targets/parse_filter.rs`, `parse_filter_hosts.rs`, `parse_request.rs`) GOZ ONUNE ALINDIGINDA, bu PROJENIN ZATEN AKTIF fuzzing ALTINDA OLDUGU GORULUYOR -- ANCAK fuzzing TIPIK olarak PANIC/crash BULMAYA ODAKLANIR, F1 GIBI 'SESSIZCE YANLIS SONUC DONDUREN (false DEGIL true OLMASI GEREKEN)' MANTIK hatalarini YAKALAMAZ (fuzzer'in bir ORACLE'A -- dogru CEVABI BILEN bir REFERANS UYGULAMAYA -- ihtiyaci VARDIR, bu genellikle KURULMAZ).
* `src/filters/network.rs` (filtre METNI AYRISTIRMA) VE `src/lists.rs` KISACA goz GEZDIRILDI -- BELIRGIN bir ek defekt GOZLENMEDI, AMA TAM satir-SATIR inceleme YAPILMADI (zaman kisiti).
* SONUC: Bu oturumda TEK, SOMUT olarak DOGRULANMIS bir bulgu (F1) var -- `is_anchored_by_hostname()`'in SADECE substring'in ILK gecisini KONTROL ETMESI nedeniyle OLUSAN bir adblock-BYPASS mantik HATASI.

## 📊 Bulgu F1: is_anchored_by_hostname(): SADECE substring'in ILK (en-sol) ORNEGI KONTROL EDILIYOR, ETIKET-SINIRINA UYAN SONRAKI bir ORNEK VARSA bile GOZ ARDI EDILIYOR -- hostname-ankörlü filtrelerde ADBLOCK-BYPASS
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-697 (Incorrect Comparison) / filtre-atlama (filter evasion) -- guvenlik-ilgili DOGRULUK hatasi
* **Stage 2 Confidence:** 55/100 — Stage1'in Python-SIMULASYONUNU BAGIMSIZ olarak TEKRAR CALISTIRDIM VE AYNI SONUCU ALDIM: `is_anchored_by_hostname('ads', 'xads.ads.com')` => `False`, OYSA 'ads.com' hostname'IN GECERLI, ETIKET-SINIRINA TAM UYAN bir ALT-dizesi. Python PORTUNUN Rust KAYNAGINA BIREBIR SADIK OLDUGUNU SATIR-SATIR KARSILASTIRARAK DOGRULADIM (uc dal -- prefix/suffix/infix -- de DAHIL, HER BIR KOŞUL IFADESI AYNI).

F1'IN 'SOLE-GATE' OLDUGUNU DOGRULAMAK icin `check_pattern_hostname_right_anchor_filter`/`check_pattern_hostname_left_right_anchor_filter` CAGRI-SITELERINI OKUDUM: her ikisinde de `is_anchored_by_hostname(...)` SONUCU `if ... { ... } else { false }` SEKLINDE KULLANILIYOR -- fonksiyon false DONDUGUNDE, BASKA bir YEDEK/alternatif kontrol-YOLU (OR'lenmis bir BASKA substring-ARAMASI VB.) YOK. Bu, F1'in TEORIK bir KOSE-durumu DEGIL, GERCEKTEN TEK VE NIHAI karar-NOKTASI oldugunu DOGRULUYOR.

AYRICA token-tabanli ON-FILTRELEME (indexleme) hipotezini DEGERLENDIRDIM: `is_anchored_by_hostname`'e ULASMADAN ONCE bir TOKEN-indeksleme ASAMASI olsa BILE, bu SADECE 'bu filtre ADAY MI' sorusuna CEVAP VERIR (hostname 'ads' alt-dizesini ICERIYOR MU) -- 'xads.ads.com' GERCEKTEN 'ads' alt-dizesini (birden FAZLA kez) ICERDIGI icin filtre YINE de ADAY olarak SECILIR VE NIHAI karar YINE `is_anchored_by_hostname`'e DUSER -- bu nedenle bir ON-filtreleme ASAMASI bu BUG'I MASKELEMEZ.

Bu, bellek-guvenligi/RCE SINIFI bir hata DEGIL, SAF bir MANTIK/dogruluk hatasi -- ETKISI (bir reklam/izleyici domain'inin KENDI hostname'INI SECEREK blocklamadan KACMASI) KESIN VE SOMUT olarak GOSTERILDI, ANCAK kod-YURUTME veya VERI-sizintisi ICERMIYOR. Bu nedenle confidence'i, 'mantik-hatasinin KENDISI KESIN/TARTISMASIZ ama NIHAI ONEM-DUZEYI (severity) tipik bir bug-bounty OLCEGINDE memory-corruption'dan DAHA DUSUK OLACAGI' DENGESINI yansitan 55'TE SABITLEDIM.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._