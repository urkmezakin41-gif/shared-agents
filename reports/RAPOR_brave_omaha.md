# Bug Bounty Raporu — brave_omaha

**Tarih:** 2026-11-05 04:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/omaha (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: C++. Description: Omaha for brave-browser.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_omaha/raw`
* **Engellenen/erişilemeyen adımlar:** Teslim edilen ~50 `omaha/base/*.h` dosyasinin HEPSI SADECE sinif/arayuz BILDIRIMLERI (declaration-only headers) -- bunlarin KARSILIK GELEN `.cc`/`.cpp` UYGULAMA dosyalari (gercek PARSE/bellek-yonetimi MANTIGININ bulundugu yerler) bu teslimde YOK. Bu nedenle bu basliklarin KORUDUGU/TANIMLADIGI sinif ARAYUZLERINDE bellek-guvenligi (buffer overflow, UAF VB.) TURU bir hata OLUP-OLMADIGI bu statik-analiz kapsaminda DOGRULANAMAZ -- sadece ARAYUZ IMZALARI/sabitler/enum'lar GORULEBILIYOR, GERCEK MANTIK DEGIL., `common/certificate_tag/certificate_tag.go`'nun Brave'e OZGU bir MODIFIKASYON mu, yoksa upstream Google/Chromium KODUNUN DOGRUDAN bir KOPYASI mi OLDUGU (hangi SATIRLARIN brave TARAFINDAN DEGISTIRILDIGI) bu teslimde BIR DIFF olarak YOK, SADECE guncel TAM dosya icerigi var -- bu nedenle 'Brave'in BU dosyada YENI bir hata INTRODUCE edip ETMEDIGI' sorusu, upstream-ile KARSILASTIRMALI bir diff OLMADAN KESIN olarak YANITLANAMADI (dosya BASLIGI 'Copyright 2015 Google Inc.' VE Apache-2.0 lisansi TASIYOR, bu da COK BUYUK olasilikla upstream-KODU OLDUGUNU GOSTERIYOR).

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] `.github/workflows/scorecard.yml`'deki iki commit diff'i -- SADECE `github/codeql-action/upload-sarif`'in PIN'LENMIS SHA'sinin surum GUNCELLEMESI (v4.38.2 -> v4.38.3 -> v4.39.0), guvenlik acisindan NOTR.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Google'in ACIK-KAYNAK 'Omaha' (Google Update) YAZILIM-GUNCELLEME istemcisinin Brave'e OZELLESTIRILMIS bir CATALI -- bu, Brave tarayicisinin WINDOWS GUNCELLEME MEKANIZMASININ TEMELI, bu nedenle critical severity ile SCOPE'TA (bir zafiyet TEDARIK-ZINCIRI/kod-yurutme RISKI TASIYABILIR).
* `build_omaha.py` (CI build-zaman scripti) satir-satir incelendi -- TUM `subprocess.check_call()` cagrilari ARGV-LISTESI FORMUNDA (shell=True DEGIL), bu nedenle shell-injection riski YOK; TUM parametreler (guid, installer adlari, tag degerleri) Brave'in KENDI CI PIPELINE'INDAN operator-SAGLANAN, SABIT/guvenilir degerler -- dis/SALDIRGAN-kontrollu girdi YOK.
* `common/certificate_tag/certificate_tag.go` (Authenticode-imzali PE/MSI binary'lere, imzayi BOZMADAN 'tag' VERISI EKLEYEN arac -- upstream Google/Chromium KODU) satir-satir incelendi -- `getAttributeCertificates()`'teki PE/COFF BASLIK AYRISTIRMA mantigi, TUM kritik noktalarda (overflow kontrolu, `certEntryEnd < certEntry.VirtualAddress`, `numDirectoryEntries > 4096` sinirlamasi, `numDirectoryEntries <= certificateTableIndex` kontrolu, dosya-sonu TUTARLILIK kontrolu) DIKKATLI SINIR KONTROLLERI ICERIYOR -- belirgin bir integer-overflow/out-of-bounds-read riski TESPIT EDILMEDI. `SetSuperfluousCertTag()`'in RSA/x509 sertifika-uretim mantigi standart Go `crypto/x509`/`crypto/rsa` kutuphanelerini KULLANIYOR, ozel/hatali bir kriptografik uygulama YOK.
* `certificate_tag_test.go` (test dosyasi) incelendi -- test-amacli ornek BINARY'LER/beklenen DAVRANISLAR ICERIYOR, odul-degeri TASIYAN bir BULGU KAYNAGI DEGIL.
* Geri kalan ~50 `omaha/base/*.h` dosyasi (ATLRegMapEx, app_util, apply_tag, browser_utils, cgi, clipboard, command_line_parser*, commands, const_*, debug, disk, encrypt, environment_*, error, etw_log_writer, event_*, extractor, file*, firewall_product_detection, highres_timer, libzip, logging*, marshal_by_value, object_factory, omaha_version, path, proc_utils, process, program_instance, queue_timer, reactor, reg_key VB.) TARANDI -- HEPSI SADECE sinif-arayuzu/sabit/enum BILDIRIMLERI, GERCEK UYGULAMA MANTIGI (.cc dosyalari) bu teslimde YOK. Bu dosyalarda KENDI BASINA bir guvenlik ZAFIYETI (SADECE bildirimlerden OLUSTUKLARI icin) tespit EDILEMEDI -- gercek bellek-guvenligi DENETIMI icin KARSILIK GELEN .cc dosyalarinin TESLIM EDILMESI GEREKIR.
* SONUC: Bu teslimde, Brave'in KENDI YAZDIGI/DEGISTIRDIGI, GERCEK UYGULAMA MANTIGI ICEREN TEK dosya `build_omaha.py` idi (incelendi, temiz) -- digger TUM icerik (header-only Omaha base siniflari + upstream certificate_tag.go + CI YAPILANDIRMASI) ya SADECE BILDIRIM ya da UZUN SUREDIR UPSTREAM'DE YOGUN SEKILDE INCELENMIS KOD. Bu NEDENLE bu teslimde YENI, odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._