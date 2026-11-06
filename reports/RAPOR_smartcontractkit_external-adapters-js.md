# Bug Bounty Raporu — smartcontractkit_external-adapters-js

**Tarih:** 2026-11-01 16:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Chainlink (https://hackerone.com/chainlink) - SOURCE_CODE Asset Identifier: https://github.com/smartcontractkit/external-adapters-js/ (structured_scope id 518185, eligible_for_bounty: true, max_severity: HIGH). Blok varlikla eslesiyor; tavan siddet High. Program sayfasi bu ortamdan dogrulanamadi.
* **Ham veri kaynağı:** `scripts/bugbounty/out/smartcontractkit_external-adapters-js/raw`
* **Engellenen/erişilemeyen adımlar:** Program sayfasi bu ortamdan dogrulanamadi; gercek saglayicilara ve gercek EA dagitimlarina istek ATILMADI. Dogrulama, repodan alinan GERCEK requester.ts ve error.ts dosyalariyla yerel sahte saglayiciya karsi yapildi (yalniz yardimci modulller - util/logger/config/metrics - minimal stub ile degistirildi; cekirdek mantik degismedi)., Saglayicinin, gecersiz sembole gercekten 200+hata govdesi dondurup dondurmedigi gercek servisle test edilmedi (customError'un varligi bu davranisi destekliyor). Hedef EA'nin internete acik olup olmadigi dagitima bagli; bu da etkiyi belirler., Bu pakette middleware'lerin cogu (cache, ws, cache-warmer) ve 8 kaynak adaptor okundu; geri kalan packages/sources/* adaptorleri okunmadi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* VALIDATOR: girdi yapilandirmasi cloneDeep'lenip varsayilan temel parametrelerle birlestiriliyor; overrides/tokenOverrides/includes istekten Map yapilarina cevriliyor (prototip kirlenmesine karsi Map kullaniliyor); tur denetimi (boolean/number/bigint/string/array/object), secenek listesi, dependsOn/exclusive kontrolleri var. shouldThrowError=false verilirse tur/secenek dogrulamasi atlaniyor (secenek-kontrollu, istekle degil). Sembol/token override'lari cagiranin kontrolunde ve belgelenmis bir ozellik.
* REQUESTER.validateResultNumber: sonucu Number() ile doniistiriyor ve yalnizca NaN ve 0 (acceptZeroValue yoksa) reddediyor. Sonuc olarak veri saglayicidan gelen Infinity (ör. '1e1000'), negatif sayilar, true (Number(true)=1) ve '0x10' gibi onaltilik dizeler gecerli sayiliyor. Bu, veri SAGLAYICI guvenine bagli bir sağlamlik eksigi; saldirgan kontrolunde olan girdi degil (saglayici yaniti). Oracle fiyat beslemesinde saglayici bozulursa asiri deger yayilabilir ama Chainlink'in coklu kaynak/medyan toplamasi bunu hafifletir -> kanitli bir istismar yolu yok.
* REQUESTER.request: yeniden deneme (RETRY), zaman asimi (varsayilan 3000 ms), axios hatalarinin siniflandirilmasi (ECONNABORTED -> 504) ve veri saglayici gecikme olcumu; zaman asimi durumunda yeniden deneme yapilmiyor. Surekli hata ureten saglayici icin ErrorBackoff middleware'i var (gelmedi).
* DOGRULAMA YONTEMI: repo'daki requester.ts ve error.ts oldugu gibi kopyalandi; yalniz ../util, ./logger, ../config, ../metrics yardimcilari minimal stub ile degistirildi. Sahte bir yerel HTTP sunucusu twelvedata'nin bilinmeyen sembol davranisini taklit etti (200 + {status:'error'}). Cikti: {"statusCode":200,"error":{"message":"... Request: {\"baseURL\":...,\"params\":{\"symbol\":\"NOSUCHSYMBOL\",\"apikey\":\"<DUMMY>\"}} ..."}} ve ANAHTAR cevap govdesinde. Stub'lar ve betik gecici dizinde (repo disi); yeniden uretim betigi PoC olarak eklenebilir.
* EA SUNUCUSU: server.ts POST baseUrl yolunda kimlik dogrulamasi YOK; sunucu trustProxy ile calisir. Hata govdesi 'statusCode: 200' ile doner (hata icinde). ErrorBackoff yalniz ayni id icin dakikada 2 hataya sinir koyar, ilk sizintiyi engellemez ve hatayi yeniden firlatir (mesaji degistirmez). Loglar icin buildCensorList var, yani anahtarlarin gizli sayildigi framework tarafindan biliniyor.
* SONUC: 1 aday bulgu (F1, Medium): sizinti zinciri gercek kodla yeniden uretildi. Siddet, EA uc noktasinin kimlere acik oldugu ve saglayicinin gecersiz girdiye hata govdesiyle donmesi dagitim/saglayici davranisina bagli; Chainlink 'high' tavanli programda bunun 'informative' sayilma riski vardir. Diger cekirdek gozlemler (Infinity/negatif sonuc kabulu) bulgu degil.

## 📊 Bulgu F1: Data-provider API key leaked in HTTP error response via Requester.generateErrorMessage (params/data included)
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** Medium
* **Zafiyet Sınıfı (CWE):** CWE-209: Generation of Error Message Containing Sensitive Information
* **Stage 2 Confidence:** 72/100 — Sizinti zinciri (params -> generateErrorMessage -> AdapterCustomError -> toJSONResponse -> HTTP cevabi) gercek repo kodu yerel sahte saglayiciya karsi calistirilarak yeniden uretildi; kod yorumu hassas verinin ayiklanmasini amacladigini soyluyor ve loglar icin censor listesi varken cevap icin yok. Kalan belirsizlik: gercek saglayicilarin gecersiz sembole 200+hata govdesi dondurmesi ve hedef EA'nin kime acik oldugu (siddeti belirler; triyajda 'informative' denebilir).

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** packages/core/bootstrap/src/lib/modules/requester.ts (generateErrorMessage, request customError path); affected adapters: twelvedata, alphavantage, fixer, currencylayer
* **Kanıt kaynağı:** `scripts/bugbounty/out/smartcontractkit_external-adapters-js/raw/ingested_incoming_2026-11-01T18-54-01_smartcontractkit_external-adapters-js.json`
* **Kanıt alıntısı:**
  ```
  [packages/core/bootstrap/src/lib/modules/requester.ts] const { baseURL, url, data, params } = config // strip noisy and sensitive data from axios config before logging/including in the response
[packages/sources/twelvedata/src/endpoint/price.ts] const params = {
    symbol,
    apikey: config.apiKey,
  }
[packages/sources/twelvedata/src/endpoint/price.ts] const customError = (data: ResponseSchema) => data.status === 'error'
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** generateErrorMessage, 'hassas veriyi ayiklar' yorumuna ragmen istegin params ve data alanlarini hata mesajina ekliyor. twelvedata/alphavantage/fixer/currencylayer adaptorleri API anahtarini params icinde gonderiyor ve customError ile saglayicinin 200+hata govdesi yanitlarini yakaliyor. Bu durumda mesaj (anahtar dahil) executeSync -> Requester.errored -> toJSONResponse ile HTTP cevabinin error.message alanina yaziliyor; server.ts bunu cagirana dondurur. Log icin censor listesi var, HTTP cevabi icin yok. Gercek requester.ts ve error.ts yerel sahte saglayiciya karsi calistirilarak dogrulandi: anahtar cevap govdesinde gorundu.
* **Nasıl Doğrulanır (Güvenli Doğrulama Adımları):**
  1. Yerel sahte saglayici (200 + {status:'error'}) ve DUMMY anahtar kullan; gercek saglayiciya istek atma.
  2. Gercek requester.ts/error.ts ile Requester.request -> new AdapterError(e) -> Requester.errored zincirini calistir.
  3. error.message icinde 'apikey' degerinin gectigini dogrula.

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
## Summary
When a data provider answers an adapter request with an application-level error (HTTP 200 plus an error body), `Requester.request()` builds the error message from the full axios request config, including `params`. Several adapters pass the provider API key in `params` (for example `apikey` for TwelveData/Alpha Vantage and `access_key` for Fixer/currencylayer). That message is returned to the HTTP caller of the external adapter in `error.message`, so the data provider API key is disclosed to whoever can call the adapter with an input that makes the provider return an error (for example an unknown symbol).

## Vulnerability Details & Root Cause
`packages/core/bootstrap/src/lib/modules/requester.ts`, `Requester.generateErrorMessage`:

```ts
const { baseURL, url, data, params } = config // strip noisy and sensitive data from axios config before logging/including in the response
...
` Request: ${JSON.stringify({ baseURL, url, data, params })},`
```

The comment states that sensitive data is stripped, but only `headers` are dropped; `params` and `data` are kept. In `Requester.request`, when `customError(response.data)` is truthy and retries are exhausted, this message becomes the message of `AdapterCustomError` / `AdapterDataProviderError`. `executeSync` (packages/core/bootstrap/src/index.ts) wraps it in `AdapterError` and returns `Requester.errored(...)` -> `toJSONResponse()`, which always includes `error.message`. `server.ts` sends that body to the caller (`res.code(status).send(result)`). The framework censors secrets in logs (`buildCensorList`), but nothing censors the HTTP response.

Affected pattern (verified in the repo): `twelvedata` (`price`, `closing`: `apikey: config.apiKey` + `customError = data.status === 'error'`), `alphavantage` (`apikey` in config params, `customError` on `Error Message`), `fixer` (`access_key`), `currencylayer` (`access_key`). The unauthenticated `POST /` route accepts the symbol/base/quote values from the request body.

## Steps to Reproduce (Safe Verification)
1. Run the unmodified `requester.ts` and `error.ts` locally against a mock provider that returns HTTP 200 with `{"code":400,"message":"**symbol** not found","status":"error"}` (no real provider traffic, dummy key).
2. Call `Requester.request({ baseURL, url: 'price', params: { symbol: 'NOSUCHSYMBOL', apikey: '<DUMMY_KEY>' } }, data => data.status === 'error')`, wrap the thrown error with `new AdapterError(e)` and serialize with `Requester.errored(...)` exactly as `executeSync` does.
3. The resulting JSON contains `"Request: {\"baseURL\":...,\"params\":{\"symbol\":\"NOSUCHSYMBOL\",\"apikey\":\"<DUMMY_KEY>\"}}"` in `error.message`, and HTTP status 200 is returned.
4. On a test deployment of the twelvedata (or alphavantage) adapter with your own key, send `{"id":"1","data":{"base":"NOSUCHSYMBOL"}}` and observe the key in the response.

## Impact
Disclosure of paid third-party data provider API keys to any party that can reach the adapter's HTTP API (adapters expose no authentication of their own) or that receives error responses from it. A leaked key allows quota exhaustion/billing abuse of the operator's provider subscription and lets an attacker call the provider as the operator. Severity depends on how exposed the adapter endpoint is.

## Recommended Remediation
Do not include `params`/`data` in `generateErrorMessage`; log them only through the censoring logger. If request details are required, redact values of known secret keys (`apikey`, `api_key`, `access_key`, `token`, ...) and the values on the censor list before building the message, and apply the same redaction to `cause`/`errorResponse` returned in `toJSONResponse()`.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._