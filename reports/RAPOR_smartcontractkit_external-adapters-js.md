# Bug Bounty Raporu — smartcontractkit_external-adapters-js

**Tarih:** 2026-11-01 15:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Chainlink (https://hackerone.com/chainlink) - SOURCE_CODE Asset Identifier: https://github.com/smartcontractkit/external-adapters-js/ (structured_scope id 518185, eligible_for_bounty: true, max_severity: HIGH). Blok varlikla eslesiyor; tavan siddet High. Program sayfasi bu ortamdan dogrulanamadi.
* **Ham veri kaynağı:** `scripts/bugbounty/out/smartcontractkit_external-adapters-js/raw`
* **Engellenen/erişilemeyen adımlar:** Program sayfasi bu ortamdan dogrulanamadi; statik inceleme, kod calistirilmadi., Gelen yalnizca CEKIRDEK (packages/core/bootstrap) 3 dosya: index.ts, lib/modules/validator.ts, lib/modules/requester.ts ve kucuk bir commit diff'i. packages/sources/* adaptorleri (asil veri saglayici entegrasyonlari, API anahtari kullanimi, girdi isleme), middleware (cache, rate-limit, cache-key, normalize), server.ts ve HTTP katmani, overrider/selector, config GELMEDI. Hukum yalnizca bu cekirdek dosyalarla sinirli.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] Requester.generateErrorMessage, hata mesajina istegin baseURL, url, data ve PARAMS alanlarini ekliyor ('hassas veriyi ayiklar' yorumuna ragmen params ve data korunuyor). customError tetiklendiginde (veri saglayici 200 ile hata govdesi dondururse) bu mesaj AdapterCustomError/AdapterDataProviderError ile cagirana DONUYOR. Eger bir adaptor API anahtarini query params ya da data icinde gonderiyorsa (header'da degil), cagiran (genelde Chainlink dugumu; bazi dagitimlarda herkese acik EA) veri saglayici anahtarini hata cevabinda gorur. Bu cekirdek kodda kanitli, ancak sizdirilacak bir anahtar icin adaptor dosyalari gerekir (gelmedi) ve cagiran cogunlukla operatorun kendisi -> kanitsiz, dusuk siddet; bulgu olarak yazilmadi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* VALIDATOR: girdi yapilandirmasi cloneDeep'lenip varsayilan temel parametrelerle birlestiriliyor; overrides/tokenOverrides/includes istekten Map yapilarina cevriliyor (prototip kirlenmesine karsi Map kullaniliyor); tur denetimi (boolean/number/bigint/string/array/object), secenek listesi, dependsOn/exclusive kontrolleri var. shouldThrowError=false verilirse tur/secenek dogrulamasi atlaniyor (secenek-kontrollu, istekle degil). Sembol/token override'lari cagiranin kontrolunde ve belgelenmis bir ozellik.
* REQUESTER.validateResultNumber: sonucu Number() ile doniistiriyor ve yalnizca NaN ve 0 (acceptZeroValue yoksa) reddediyor. Sonuc olarak veri saglayicidan gelen Infinity (ör. '1e1000'), negatif sayilar, true (Number(true)=1) ve '0x10' gibi onaltilik dizeler gecerli sayiliyor. Bu, veri SAGLAYICI guvenine bagli bir sağlamlik eksigi; saldirgan kontrolunde olan girdi degil (saglayici yaniti). Oracle fiyat beslemesinde saglayici bozulursa asiri deger yayilabilir ama Chainlink'in coklu kaynak/medyan toplamasi bunu hafifletir -> kanitli bir istismar yolu yok.
* REQUESTER.request: yeniden deneme (RETRY), zaman asimi (varsayilan 3000 ms), axios hatalarinin siniflandirilmasi (ECONNABORTED -> 504) ve veri saglayici gecikme olcumu; zaman asimi durumunda yeniden deneme yapilmiyor. Surekli hata ureten saglayici icin ErrorBackoff middleware'i var (gelmedi).
* SONUC: Okunan 3 cekirdek dosyada yamasiz, kod kanitli bir zafiyet BULUNAMADI. Asil guvenlik yuzeyi (adaptorler, HTTP sunucusu, cache anahtari, rate-limit, websocket) gelmedi; 'bulgu yok' yalnizca okunan dosyalar icin gecerlidir.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._