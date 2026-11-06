# Bug Bounty Raporu — coinbase_prime-sdk-go

**Tarih:** 2026-11-02 21:38 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/prime-sdk-go, Coinbase Prime REST API icin Go istemci SDK'si).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_prime-sdk-go/raw`
* **Engellenen/erişilemeyen adımlar:** Gercek imzalama/HTTP cagri dongusunun bir kismi github.com/coinbase/core-go (harici paket) icinde - bu pakedin kaynagi GELMEDI, sadece bu depodaki sarmalayici (AddPrimeHeaders/sign) incelenebildi., Dosyalarin buyuk kismi (activities/balances/financing/futures/vb.) otomatik-uretilmis ince REST cagri sarmalayicilari ve model/errors/*_gen.go (77KB info_gen.go dahil) kod-uretim ciktisi - tek tek incelenmedi, orneklenerek tarandi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* client/rest.go AddPrimeHeaders/sign(): HMAC-SHA256 imzalama (timestamp+method+path+body), prime-sdk-ts'de (bu oturumda daha once incelenen ve temiz bulunan) AYNI semaya tam uyumlu ve dogru uygulanmis. Credentials (AccessKey/Passphrase/SigningKey) sadece header olusturmada kullaniliyor, loglanmiyor.
* credentials/credentials.go: ReadEnvCredentials/UnmarshalCredentials basit JSON parse, secret deger yazdirma/loglama yok.
* model/errors/parse.go: standart encoding/json kullanimi, enjeksiyon riski yok.
* Bu SDK, bu oturumda daha once incelenen coinbase/prime-sdk-ts (TypeScript esdegeri) ile AYNI kalite ve tasarim desenini tasiyor; HMAC imzalama dogru, secret yonetimi temiz.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._