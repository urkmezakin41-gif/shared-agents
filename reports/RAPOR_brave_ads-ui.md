# Bug Bounty Raporu — brave_ads-ui

**Tarih:** 2026-11-05 09:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/ads-ui (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Self-service ads UI.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_ads-ui/raw`
* **Engellenen/erişilemeyen adımlar:** Repo COK BUYUK (100'den fazla .tsx/.ts dosyasi) -- ZAMAN KISITI nedeniyle TUM dosyalar satir-SATIR incelenemedi. INCELEME, EN YUKSEK-DEGERLI alanlara (auth/magic-link akisi, URL-dogrulama/onizleme render'i, odeme/checkout CAGRILARI) ODAKLANDI. src/routes/campaigns/analytics/* (metrik/grafik gosterimi), src/components/Creatives/CreativeForm.tsx (TAM form MANTIGI), VE src/graphql-client/* TAM detayli incelenmedi., Hedefin GERCEK YETKILENDIRME/IS-MANTIGI DOGRULAMASI (orn. odeme TUTARLARININ, kampanya SAHIPLIGININ, URL-DOGRULAMASININ GERCEK UYGULANMASI) SUNUCU-tarafinda (ad-server backend, bu teslimde YOK) -- client-tarafi KOD, SADECE bu sunucuya YAPILAN cagrilari ICERIYOR, bu nedenle IDOR/yetkilendirme-BYPASS TURU bulgular bu teslimin DOGASI GEREGI GORULEMEZ.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki commit diff'i (Node.js SURUM bump'i VE pnpm/typescript-eslint/react-window BAGIMLILIK GUNCELLEMELERI) -- SADECE rutin TOOLCHAIN/bagimlilik GUNCELLEMESI, guvenlik acisindan NOTR.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Ads icin SELF-SERVICE reklamveren PANELI (kayit, giris, kampanya/creative OLUSTURMA, odeme, analitik). Auth AKISI (`src/auth/lib/index.ts`, `useAuthorize.ts`, `AuthVerify.tsx`, `MagicLink.tsx`), URL-DOGRULAMA/onizleme RENDER'i (`UrlResolver.tsx`, `use-url-validation.ts`, `SearchPreview.tsx`, `NotificationPreview.tsx`) VE odeme/checkout CAGRILARI (`checkout/lib/index.ts`, `useCreatePaymentSession.ts`, `useIncreaseCampaignBudget.ts`) ONCELIKLI olarak incelendi.
* Auth akisi SADECE cookie-tabanli oturum (`credentials: 'include'`) KULLANIYOR, token'lar localStorage'da GORULMEDI. Magic-link DOGRULAMASI (`AuthVerify.tsx`) URL'deki `code`/`id`'yi SADECE bir KULLANICI TIKLAMASI ILE (otomatik DEGIL) sunucuya GONDERIYOR -- bu, e-posta/anti-phishing TARAYICI botlarinin linki ERKEN TUKETMESINE karsi IYI-BILINEN bir SAVUNMA DESENI.
* `SearchPreview.tsx::href={targetUrl}` -- ARASTIRILAN VE CURUTULEN bir HIPOTEZ: `targetUrl` (reklamverenin KENDI landing-page URL'si) dogrulanmadan `new URL()` VE `<a href>`'e VERILIYOR, teorik olarak `javascript:` SEMASI ICEREBILIR. ANCAK (1) bu, SADECE reklamverenin KENDI formuna YAZDIGI bir deger (self-XSS SINIRLI saldirgan-modeli), (2) link `target='_blank' rel='noreferrer noopener'` ile ACILIYOR -- bu, TIKLANDIGINDA (eger tarayici javascript: URI'yi YENI SEKMEDE calistirmaya IZIN VERSE bile) YENI, izole bir about:blank BAGLAMINDA calisir, `noopener` nedeniyle `window.opener`'a ERISIMI YOK -- orijinal ads-ui SAYFASININ cookie/DOM'una ERISEMEZ. `use-url-validation.ts` da ZATEN sunucuya SADECE `https://` ile BASLAYAN URL'leri GONDERIYOR (istemci-tarafi UX kontrolu). SONUC: GOSTERILEBILIR bir ETKI YOK, bulgu olarak SUNULMADI.
* `dangerouslySetInnerHTML`/`innerHTML`/`eval`/`new Function` icin TUM teslimde GENIS-CAPLI grep YAPILDI -- SIFIR SONUC. TUM `window.open()` CAGRILARI SABIT, HARDCODED Brave-KONTROLLU URL'lere (orn. `brave.com`, `ads-help.brave.com`) GIDIYOR VE TUMU `noopener` KULLANIYOR -- reverse-tabnabbing ONLENMIS.
* `checkout/lib/index.ts` -- TUM odeme/checkout FONKSIYONLARI (createPaymentSession, validatePaymentSession, increaseCampaignBudget) SADECE ad-server backend'ine YAPILAN ince (thin) API CAGRILARI; GERCEK TUTAR/yetkilendirme DOGRULAMASI SUNUCUDA (bu teslimde YOK) OLMASI GEREKEN, BEKLENEN bir TASARIM -- client-tarafi kod, bir TUTAR-manipulasyonu ZAFIYETINI KENDI BASINA SERGILEMIYOR.
* SONUC: Incelenen EN YUKSEK-ONCELIKLI alanlarda (auth, magic-link, URL-onizleme/dogrulama, odeme-cagrilari), odul-degeri TASIYAN YENI bir client-tarafi guvenlik bulgusu TESPIT EDILEMEDI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._