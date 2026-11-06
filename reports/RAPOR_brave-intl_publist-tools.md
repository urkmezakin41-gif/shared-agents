# Bug Bounty Raporu — brave-intl_publist-tools

**Tarih:** 2026-11-04 00:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave-intl -> https://github.com/brave-intl/publist-tools (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave-intl_publist-tools/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Rewards'in gizlilik-koruyucu yayinci-dogrulama prefix-listesi (Chrome Safe Browsing'e benzer bir tasarim) ile etkilesim kurmak icin gelistiricilerin KULLANDIGI YEREL bir CLI araci (`publist-tools fetch`/`search`) -- ag-uzerinden erisilebilir bir servis DEGIL, Brave calisanlarinin kendi makinesinde cagirdigi bir hata-ayiklama/sorgu araci.
* Son iki commit TAMAMEN bagimlilik guncellemesi (protobufjs 8.6.6->8.8.0) -- KOD MANTIGI degisikligi YOK, iki ozdes commit (goruldugu kadariyla).
* F1 disinda, `channel_reader.js`'in `unpad()` fonksiyonu (4-bayt buyuk-endian uzunluk onegi okuma + slice) incelendi -- Node.js Buffer.slice() sinirlarin disindaki uzunluklari KIRPAR (crash etmez), bu nedenle bellek-guvenligi acisindan sorun yok; en kotu durumda `decompress()` zaten yakalanan bir hata firlatir ('Error decompressing channel response data').
* `cli.js`'deki argument ayristirma (`parseCommand`) basit ama yalnizca YEREL CLI argumanlarini isliyor (operatorun kendi girdigi komut satiri) -- ucuncu-taraf saldirgan girdisi yok.
* SONUC: Bu KUCUK, yerel bir CLI gelistirici aracinda GERCEK ama DUSUK siddette bir mantik hatasi (F1, atama/karsilastirma karisikligi) tespit edildi -- saldiri yuzeyi doğasi geregi cok dar (yerel arac, saldirgan kontrolu yok, canli bir guvenlik sinirini etkilemiyor).

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 20 | REJECT | F1, JavaScript dilinin KENDI semantigiyle dogrulanan, KUSKUYA YER BIRAKMAYACAK sekilde GERCEK bir hata (atama vs karsilastirma) -- ancak HackerOne-raporlanabilir bir guvenlik acigi barajini GECMIYOR: (1) `publist-tools` TAMAMEN YEREL bir CLI gelistirici araci -- ag-uzerinden erisilebilir bir servis veya Brave'in tarayicisindaki CANLI bir guvenlik kontrolu DEGIL; Brave'in GERCEK yayinci-dogrulama mantigi (tarayicinin KENDISINDE) TAMAMEN AYRI bir kod tabaninda (brave-core, C++) uygulanir, bu JS araci sadece HATA-AYIKLAMA/sorgu amaclidir. (2) Saldirganin bu hatayi TETIKLEMESI icin kontrol edebilecegi HICBIR girdi yok -- tetiklenmesi icin sunucunun GELECEKTE/BAZEN BROTLI-DISI bir `compressionType` DONDURMESI gerekir, bu da bu aracin KULLANICISININ (Brave gelistiricisinin) kontrolunde DEGIL. (3) Etki, bu YEREL aracin hata-ayiklama CIKTISININ yanlis olmasi -- hicbir kullanici fonu, verisi veya canli guvenlik siniri etkilenmiyor. Confidence=20, hint-tier'e yonlendiriliyor -- ucuz, tek-satirlik bir duzeltme (`=` -> `===`) olarak bakim ekibine iletilmeye deger, ama tam rapor/HackerOne submission seviyesinde degil. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._