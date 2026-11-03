# Bug Bounty Raporu — coinbase_core-ts

**Tarih:** 2026-11-03 01:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/core-ts - prime-sdk-ts ve coinbase-wallet-sdk disindaki diger TS SDK'larin bagimli oldugu paylasilan HTTP cekirdek kutuphanesi; onceki iki turda eksik bagimlilik olarak not edilmisti, bu turda geldi).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_core-ts/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* http/tls.ts::buildHttpsAgent(): rejectUnauthorized SADECE cagiran taraf AÇIKÇA bir deger verirse ayarlaniyor; HICBIR YERDE sabit-kodlu 'rejectUnauthorized: false' veya varsayilan TLS dogrulamasini devre disi birakma yok. mTLS materyali (cert/key/ca/pfx/passphrase) sadece https.Agent'a geciriliyor, loglanmiyor.
* http/coinbaseHttpRequest.ts: this.fullUrl (SORGU DIZESI DAHIL) imzalama fonksiyonuna ('generateAuthHeaders') geciliyor - BU, prime-sdk-go/py'deki 'sadece path, sorgu haric' semasindan FARKLI gorunuyor. ANCAK prime-sdk-ts'nin kendi credentials/index.ts'i (onceki turda incelendi) generateAuthHeaders icinde 'new URL(uri).pathname' kullanarak sorgu dizesini ZATEN kendisi ayikliyor - yani NIHAI imzalanan mesaj GENE sadece path+body, ailenin digerleriyle TUTARLI. Cross-paket bir asimetri YOK.
* serialization/jsonUtility.ts: yalniz JSON.stringify/JSON.parse etrafinda ince bir sarmalayici; rekursif merge/assign yapmiyor, bu yuzden prototip kirletme riski (coinbase-wallet-sdk'nin 'toCamelCase' fonksiyonu icin not edilen tur) BU dosyada uygulanamaz.
* http/httpClient.ts: apiBasePath constructor'da sabitleniyor (istek-bazinda degistirilemiyor), axios-retry yapilandirmasi standart; per-call client olusturma transformer'larin sizmasini onlemek icin ayrı ele alinmis.
* error/index.ts::handleException: hata mesajlari SADECE sunucunun kendi response/reason verisini iceriyor; kimlik bilgisi/secret hic dahil edilmiyor.
* Bu paket, bu oturumda incelenen diger Coinbase TS/Go/Python HTTP cekirdek kutuphaneleriyle (core-go, prime-sdk-ts/go/py) AYNI kalite ve tasarim desenini tasiyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._