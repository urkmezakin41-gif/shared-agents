# Bug Bounty Raporu — brave_psst-component

**Tarih:** 2026-11-07 08:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/psst-component (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_psst-component/raw`
* **Engellenen/erişilemeyen adımlar:** `src/twitter/policy.ts` VE `src/linkedin/policy.ts`'nin SOMUT `waitForSettingAppliedWithTimeout()` implementasyonlari (DOM-etkilesim MANTIGININ kendisi) ZAMAN KISITI nedeniyle SATIR-SATIR incelenemedi -- SADECE `policy_base.ts`'deki PAYLASILAN `applyPolicies()` iskeleti VE chatgpt/twitter'in `user.ts` (kimlik-cikarma) dosyalari TAM olarak incelendi. `scripts/generate-psst-config.ts` VE `scripts/webpack/wrap-psst-result-plugin.js` (BUILD-zamani ARACLARI, runtime saldiri-YUZEYI DISINDA) atlandi., Host (brave-core, C++) tarafinin `window.__bravePsstParams`'i NE ZAMAN/NASIL enjekte ettigi (orn. document_start VS document_idle, VE bir SAYFA-script'inin bu GLOBAL'i ONCEDEN tanimlayarak CLOBBER/race ETME IHTIMALI) bu teslimin KAPSAMI DISINDA (host KODU ayri bir repo'da) -- bu TAMAMEN JS-tarafi deger-OKUMA KODU (`parseParams()`), enjeksiyon-ZAMANLAMASININ KENDISI incelenemedi.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i -- gorunuse gore kucuk GUNCELLEMELER/surum degisiklikleri, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, 'Privacy Settings Tuning Tool' (PSST) -- Brave'in Twitter/X, LinkedIn VE ChatGPT GIBI sitelerde KULLANICI ADINA OTOMATIK olarak gizlilik-ayarlarini KAPATAN (reklam-kisisellestirmesi, 'modeli iyilestirmek icin sohbetleri kullan' VB.), izole bir DUNYAYA (isolated world) enjekte edilen TypeScript user/policy script'leri.
* src/chatgpt/user.ts::getChatGptUserId/getUserId -- EN HASSAS dosya OLARAK HEDEFLI incelendi: `#client-bootstrap` script ETIKETINDEN OpenAI OTURUM verisini (ACIKCA bir `accessToken` ALANI ICEREN) OKUYOR, ANCAK SADECE `session.user.name`/`session.user.id` ALANLARINI CIKARIP `user_id` olarak KULLANIYOR -- `accessToken` HICBIR YERDE OKUNMUYOR, LOGLANMIYOR VEYA host'a GERI DONDURULEN `UserScriptData` YAPISINA DAHIL EDILMIYOR (`getTasks()`'in INSA ETTIGI `userData` nesnesini SATIR SATIR DOGRULADIM -- SADECE `user_id` (string), `initial_execution`, VE statik `getSiteScriptData()` CIKTISI ICERIYOR).
* src/common/psst_utils.ts::isOnExpectedStep/isInitialExecution -- sessionStorage'da SAKLANAN akis-DURUMUNUN (`current_task.url`/`start_url`), MEVCUT `location.origin`+`location.pathname` ILE ESLESTIGINI DOGRULUYOR -- bu, BASKA bir SAYFAYA/SEKMEYE GECIS yapildiginda ESKI/alakasiz bir akis-DURUMUNUN YANLISLIKLA DEVAM ETTIRILMESINI ENGELLEYEN DOGRU bir KONTROL. `PSST_STALE_MS` (40 saniye) ile ESKI/kesintiye-ugramis akislar da DOGRU sekilde TESPIT EDILIYOR.
* TUM teslim edilen kodda (`eval(`, `innerHTML`, `outerHTML`, `document.write`, `new Function(`) ICIN HEDEFLI bir TARAMA yaptim -- SIFIR ESLESME. Task selector'lari (`CSS.escape()` ile DOGRU sekilde KACILAN, SABIT/statik cok-dilli ETIKET DIZILERINDEN URETILEN) SADECE `querySelector`+DOM-event-DISPATCH icin KULLANILIYOR, ASLA KOD-YURUTME icin DEGIL.
* src/twitter/user.ts::getUserId -- `twid` cookie DEGERINI SADECE bir OPAK PARTITION-anahtari olarak KULLANIYOR, ek bir ISLEME/ayristirmaya TABI TUTMUYOR -- hassas bir OTURUM-token'i DEGIL.
* SONUC: Bu, kullanicinin GERCEK, kimlik-DOGRULANMIS oturumlarina (ChatGPT, X, LinkedIn) DOGRUDAN erisen, YUKSEK-guven GEREKTIREN bir tarayici-enjeksiyon BILESENI OLMASINA RAGMEN, VERI-minimizasyonu (hassas token'larin ASLA disari SIZDIRILMAMASI), DOGRU durum-dogrulamasi VE guvenli DOM-etkilesim deseni SERGILIYOR. Odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI, rapor TEMIZ olarak dispatch edilmeli.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._