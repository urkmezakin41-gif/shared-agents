# Bug Bounty Raporu — coinbase_prime-sdk-ts

**Tarih:** 2026-11-02 07:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/prime-sdk-ts, TypeScript client SDK).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_prime-sdk-ts/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; derlenip calistirilmadi., Kritik bagimliliklar GELMEDI: src/shared/toCamelCase.ts (API cevabini camelCase'e ceviren fonksiyon - prototip kirletme riski icin gerekli), src/shared/envUtils.ts (createCredentialsFromEnv/mergeClientOptionsFromEnv - PRIME_CREDENTIALS env var JSON parse + mTLS ayarlari), @coinbase/core-ts paketi (gercek HTTP transport katmani - CoinbaseClient.request). Bu dosyalar olmadan asil ag/guven sinirlari (TLS/mTLS dogrulamasi, prototip kirletme) dogrulanamadi., Tam-repo agac taramasi cogunlukla otomatik uretilmis model/*.ts tip tanimlari (yaklasik 90+ dosya) getirdi; bunlar veri tipi tanimlari oldugundan tek tek incelenmedi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* credentials/index.ts: CB-ACCESS-* HMAC-SHA256 imzalama (Coinbase Exchange/Prime standart semasi: timestamp+method+path+body) dogru uygulanmis; secretKey yalniz crypto.createHmac icinde kullaniliyor, loglanmiyor. Kimlik bilgisi eksikse kibarca 'yalniz public endpoint' uyarisi basiyor (secret/passphrase deger olarak YAZDIRILMIYOR).
* errors/index.ts (wrapAsPrimeException/parsePrimeErrorBody): hata govdesi SADECE API SUNUCUSUNUN dondugu response.data'dan olusturuluyor; istek govdesi/kimlik bilgileri hata nesnesine kopyalanmiyor - secret sizma riski yok.
* client.ts (CoinbasePrimeClient): apiBasePath disaridan override edilebiliyor (SDK kullanicisi kendi base URL'ini verebilir) - bu TASARIM GEREGI (test/sandbox ortamlari icin), SSRF degil; zaten SDK'yi cagiran taraf zaten tam agirlikli HTTP istegi yapma yetkisine sahip (kendi kodu).
* apiSpec/generate*.js (kod uretim script'leri): eval/exec/child_process yok; yalnizca Coinbase'in kendi API spec YAML dosyasini (repo icinde, saldirgan kontrolu disinda) okuyup TS/dokumantasyon uretiyor - build-time, kullanici girdisi almiyor.
* constants.ts: API_BASE_PATH sabit https://api.prime.coinbase.com/v1/ (HTTPS, dogru).
* Bu bir ISTEMCI SDK'si (sunucu degil); gercek saldiri yuzeyi (TLS dogrulamasi, mTLS sertifika isleme, API cevabi uzerinde prototip kirletme) eksik dosyalarda (@coinbase/core-ts, shared/toCamelCase.ts, shared/envUtils.ts). Bu dosyalar gelirse yeniden degerlendirilebilir.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._