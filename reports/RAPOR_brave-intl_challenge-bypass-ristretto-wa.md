# Bug Bounty Raporu — brave-intl_challenge-bypass-ristretto-wa

**Tarih:** 2026-11-03 23:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave-intl -> https://github.com/brave-intl/challenge-bypass-ristretto-wasm (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Rust. Description: A WASM crate to expose functionality from challenge-bypass-ristretto.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave-intl_challenge-bypass-ristretto-wa/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in `challenge-bypass-ristretto` Rust kripto crate'ini (Privacy Pass / VOPRF token protokolu -- onceki bir oturumda RFC 9497 HashToGroup/Finalize ve NIZK DLEQ ispati ACISINDAN zaten DOGRU bulunmustu) WebAssembly araciligiyla TARAYICIYA acan KUCUK bir sarmalayici (wrapper) crate'i. README ACIKCA 'client side use only... inappropriate for backend use... no constant-time guarantees in WASM' diyor -- yani sadece ISTEMCI-TARAFI (tarayici icinde) kullanim icin tasarlanmis, kendi guvenlik sinirlarini ACIKCA belgeleyen bir kutuphane.
* Son iki commit: (1) CI/versiyon-tutarliligi kontrolu + upstream `challenge-bypass-ristretto` crate'inin 2.0.3->2.0.4 surum guncellemesi (changelog/degisiklik icerigi bu teslimde yok, ancak bu sarmalayicinin KENDI mantiginda bir degisiklik degil); (2) `cargo audit` CI is-akisi eklenmesi + bagimlilik guvenlik-yama guncellemeleri (subtle 2.4.1->2.6.1, zeroize 1.3.0->1.8.2 -- ikisi de dogrudan GUVENLIK-ILGILI kutuphaneler, 'sabit-zamanli karsilastirma' ve 'bellek sifirlama' icin kullanilir) + Cargo workspace yeniden-duzenlemesi + salt bicimlendirme (import siralamasi) degisiklikleri -- GUVENLIK MANTIGI acisindan onemli olan tek sey bagimlilik surum yukseltmeleri, bu sarmalayicinin KENDI kodunda mantik degisikligi YOK.
* F1 disinda, dosyanin TUMU (tek dosya, ~190 satir) satir-satir incelendi: `cbr-macros`'in uretti gi otomatik `encode_base64`/`decode_base64` implementasyonlari dogru hata-donusumu kullaniyor; `SigningKey::sign`, `rederive_unblinded_token`, `VerificationKey::sign_sha512`/`verify_sha512` metotlari dogrudan upstream crate'e delege ediyor (ozel kriptografi YOK); `Token::random()`/`SigningKey::random()` `OsRng` kullaniyor (dogru, kriptografik-guvenli RNG kaynagi).
* SONUC: Bu KUCUK sarmalayici crate'de bir gercek, dusuk-orta siddette hata-isleme tutarsizligi bulgusu (F1) tespit edildi -- kriptografik mantigin kendisi degil, HATA YOLU davranisi etkileniyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 25 | REJECT | F1 kod-okumasiyla DOGRULANABILIR gercek bir hata (5 `.unwrap()` ornegi, dosyanin digerleriyle TUTARSIZ) -- ancak HackerOne-raporlanabilir bir guvenlik acigi barajini TAM GECMIYOR: (1) Bu fonksiyonlarin CAGIRANI, bu KUCUK WASM sarmalayicisini ENTEGRE EDEN Brave'in KENDI (ilk-taraf) odul/reklam istemci kodu olmasi en olasi senaryo -- bu REPO'nun KENDISI entegrasyon kodunu icermiyor, bu nedenle rastgele bir web sayfasinin/UCUNCU-TARAF saldirganin bu WASM fonksiyonlarina DOGRUDAN, keyfi girdilerle erisebildigine dair KANIT YOK (missing integration context). (2) GERCEKCI tetikleyici senaryo (Brave'in KENDI odul sunucusunun bozuk/beklenmedik bir yanit gondermesi) ZATEN YARI-GUVENILIR bir bilesen tarafindan tetikleniyor -- klasik 'ucuncu-taraf saldirgan' modeli degil. (3) Etki, bellek bozulmasi/kripto-atlatma DEGIL, sadece bir WASM trap/panik (DoS, muhtemelen o ORNEGIN yeniden baslatilmasini gerektiriyor) -- kullanicinin fonlarini/verilerini etkilemiyor. Bu, onceki oturumda benzer sekilde degerlendirilen 'gercek ama dar-etkili/belirsiz-saldirgan-erisimli' bulgu sinifina (orn. base_benchmark F1, base_skills F1) uyuyor. Confidence=25, hint-tier'e yonlendiriliyor -- tam rapor/HackerOne submission seviyesinde degil, ama bakim ekibine iletilmeye deger bir kod-kalitesi/dayaniklilik duzeltmesi. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._