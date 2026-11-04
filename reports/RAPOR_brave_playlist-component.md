# Bug Bounty Raporu — brave_playlist-component

**Tarih:** 2026-11-04 19:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/playlist-component (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_playlist-component/raw`
* **Engellenen/erişilemeyen adımlar:** Bu repo SADECE sayfaya-enjekte-edilen JS kaynagini (index.js, youtube.com.js, media_source_api_suppressor.js) iceriyor -- bu scriptlerin `onMediaDetected(medias)` araciligiyla gonderdigi veriyi ALAN NATIVE (C++/Swift/Kotlin, brave-core/brave-ios/brave-android depolarinda) TUKETICI kod bu teslimde YOK. Bu nedenle 'title/author/thumbnail gibi SAYFA-KAYNAKLI metinler, NATIVE tarafta bir DOSYA-ADI/yol olarak KULLANILIYORSA path-traversal riski olusturabilir mi' sorusu bu kapsamda DOGRULANAMADI -- bu SADECE teorik bir asagi-akis notu, bu JS'in KENDISINDE bir bulgu DEGIL.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave tarayicisinin 'Playlist' (cevrimdisi medya oynatma) ozelligi icin sayfaya enjekte edilen KUCUK bir JavaScript bilesen seti -- `index.js` (genel medya-tespiti), `youtube.com.js` (YouTube'a OZEL meta-veri cikarma, `window.ytplayer`'dan), `media_source_api_suppressor.js` (MediaSource API'sini devre-disi birakma), `playlist_exclusions.json` (YouTube arama/kanal sayfalari gibi bazi URL-yollarini HARIC TUTAN basit bir kural dosyasi).
* Iki commit diff'i incelendi: (1) `playlist_exclusions.json`'un YENI EKLENMESI -- YouTube'un `/results`, `/feed`, `/@...` yollarinin 'medya iceren sayfa' olarak YANLIS-POZITIF tespit edilmesini onleyen bir UX-duzeltmesi, guvenlik-ilgisiz; (2) SALT CI/CodeQL action versiyon-guncellemesi. Her ikisi de guvenlik acisindan NOTR.
* `index.js`'teki `fixUpUrl()`/`isHttpsScheme()` cift-katmanli URL-dogrulamasi OZELLIKLE dikkatle incelendi: HER turlu kaynak-URL (medya `src`'si, thumbnail) HTTPS-ONLY bir kisitlamadan GECIYOR -- `blob:` SADECE `blob:https://...` formunda KABUL ediliyor, DIGER TUM semalar (`http:`, `file:`, `javascript:`, `data:`) REDDEDILIYOR. Protokol-GORELI bir URL (`//evil.com/x.jpg`) veya kok-GORELI bir yol (`/vi/x.jpg`) ile olasi bir CURUTME DENENDI: HER IKISI de `window.location` (HER ZAMAN https, calistirilan SAYFA'nin KENDISI) BAZ ALINARAK cozumleniyor, bu nedenle NIHAI SONUC HER ZAMAN GECERLI bir https:// URL'si oluyor (protokol-goreli durumda, teorik olarak farkli bir HOST'A -- orn. evil.com -- CIKABILIR, AMA bu, saldirganin DOGRUDAN MANIPULE EDEMEDIGI, YouTube'un KENDI `window.ytplayer` API-yanitindan gelen bir deger ICIN gecerli, yani bu teorik yol GERCEKCI bir saldirgan-SENARYOSU OLUSTURMUYOR).
* `isMediaSourceObjectURL()`'deki `fetch(src)` cagrisinin, SADECE AYNI-SAYFANIN KENDI `blob:` URL'sine (same-origin, sayfa tarafindan ZATEN olusturulmus) yapildigi dogrulandi -- cross-origin bir veri-sizdirma/SSRF riski YOK.
* Genis-capli grep taramasi: `eval(`, `innerHTML`, `document.write(`, `new Function(` -- HICBIRI bu KUCUK kod-tabaninda bulunamadi.
* SONUC: Bu KUCUK, basit sayfaya-enjekte-edilen JS bilesen setinde HICBIR guvenlik acigi tespit edilmedi. Teslim edilen kapsamin KENDISI cok SINIRLI (native tuketici kodu YOK) -- bu nedenle 'bu veri NATIVE tarafta nasil kullaniliyor' sorusu ACIK kalan bir kapsam-sinirlamasi olarak NOT EDILDI, ama bu JS'in KENDI dogrulama mantigi SAGLAM bulundu.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._