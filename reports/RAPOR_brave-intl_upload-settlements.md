# Bug Bounty Raporu — brave-intl_upload-settlements

**Tarih:** 2026-11-03 21:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave-intl -> https://github.com/brave-intl/upload-settlements (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: a repo for facilitating the uploading of settlements.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave-intl_upload-settlements/raw`
* **Engellenen/erişilemeyen adımlar:** Eyeshade backend'inin (`/v2/publishers/settlement` uc noktasi) kendi kod tabani teslim edilen veride YOKTU -- bu aractan gonderilen settlement verisinin eyeshade tarafinda NASIL yetkilendirildigini/dogrulandigini (orn. negatif `probi` degerlerine izin verilip verilmedigini) KESIN olarak dogrulayamadim. Bu nedenle 'negatif sayisal alan' gozlemi bir BULGU olarak degil, sadece bir analist notu olarak kaydedildi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in hazirlanmis settlement (odeme) dosyalarini eyeshade backend'ine YUKLEYEN DAHILI bir CLI araci -- AG-UZERINDEN erisilebilir bir servis DEGIL, Brave operatorlerinin kendi makinelerinde kendi `--auth`/`--file`/`--url` CLI argumanlariyla calistirdigi bir toplu-is (batch) scripti. Bu, saldiri yuzeyini COK daralTAN bir mimari (ag-erisimi yok, girdi dosyalari 'baska bir settlement araci' tarafindan yerel olarak uretilmis, kullanici kendi secimi).
* Son iki commit TAMAMEN bagimlilik guncellemesi (lodash 4.17.21->4.17.23, call-bind ailesinin call-bound/side-channel-* paketlerine gecisi) -- KOD MANTIGI degisikligi YOK.
* `index.js`'in Joi dogrulamasi (`txsValidator`) incelendi: `probi`/`amount`/`fees`/`commission`/`fee` alanlari icin kullanilan `numeric` kurali (`^-?(\d+(\.\d*)?|\.\d+)(e[+-]?\d+)?$`) NEGATIF degerlere izin veriyor -- teorik olarak 'negatif bir BAT odeme tutari' bu arac TARAFINDAN reddedilmeyip eyeshade'e iletilebilir. ANCAK bu aracin girdisi saldirgan-kontrollu DEGIL (yerel, operator-secilmis dosyalar), ve GERCEK yetkilendirme/is-mantigi siniri eyeshade backend'inde (bu depoda YOK) olmali -- bu nedenle bu, bu ARACIN kendisinde raporlanabilir bir guvenlik acigi degil, sadece upstream-veri-kalitesi/defense-in-depth notu.
* `getFiles()`'daki path birlestirmesi (`path.join(__dirname, target, file)`) CLI argumanlarindan geliyor, ancak bu argumanlari SAGLAYAN kisi aracin KENDI OPERATORU (kendi makinesinde kendi komutunu yazan guvenilir bir kisi) -- path-traversal icin bir ucuncu-taraf saldirgan senaryosu yok.
* `merge()` fonksiyonu lodash `_.merge`'u eyeshade API YANITINI (`body`, guvenilir backend yaniti) yerel bir `output` degiskenine birlestirmek icin kullaniyor -- ancak `output` hic bir yerde yazilmiyor/donduruluyor/kullanilmiyor (olu kod); yine de, kaynak GUVENILIR backend yaniti oldugundan prototype-pollution riski (lodash merge'un bilinen `__proto__` zafiyeti) saldirgan tarafindan tetiklenebilir DEGIL.
* SONUC: Bu, saldiri yuzeyi dogasi geregi COK DAR (ag-erisimi olmayan, guvenilir-operator CLI araci) bir hedefte, HackerOne-raporlanabilir bir guvenlik acigi TESPIT EDILEMEDI. Temiz rapor (findings=[]) teslim ediliyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._