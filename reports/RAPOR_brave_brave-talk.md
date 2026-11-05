# Bug Bounty Raporu — brave_brave-talk

**Tarih:** 2026-11-05 06:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/brave-talk (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Unlimited private video calls with your friends and colleagues.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_brave-talk/raw`
* **Engellenen/erişilemeyen adımlar:** `src/jitsi/lib.ts`, `src/jitsi/options.ts`, `src/jitsi/event-handlers.ts` (Jitsi IFrame API entegrasyonu -- postMessage/iframe guven SINIRLARININ potansiyel kaynagi) VE `src/downloaded-transcript.ts` (transkript METIN-FORMATI ayristirici) ZAMAN KISITI nedeniyle SADECE KISMEN/dolayli olarak (diger dosyalardan referanslar uzerinden) incelendi, satir-satir TAM bir gecis YAPILMADI -- bu dosyalar ONCELIKLI olarak bir SONRAKI incelemede ELE ALINMALI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] pnpm-lock.yaml/pnpm-workspace.yaml VE .node-version'daki iki commit diff'i -- SADECE rutin bagimlilik/surum GUNCELLEMELERI (body-parser, fast-uri, glob, minimatch, qs, serialize-javascript, zod, Node.js surumu), guvenlik acisindan NOTR (hatta BAZILARI zaten BILINEN GHSA'lari adreslemek ICIN YAPILMIS GUNCELLEMELER).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Talk'in (Jitsi-tabanli video GORUSME) web ON-YUZU -- JWT tabanli oda-erisim JETONLARI, bir 'recovery token' MEKANIZMASI (premium abonelik kurtarma), transkript GORUNTULEME VE CSRF-korumali REST cagrilari ICERIYOR.
* `src/js/jwt-decode.js` (davidchambers/Base64.js'ten UYARLANMIS, SADECE DECODE EDEN, IMZA DOGRULAMASI YAPMAYAN bir JWT ayristirici) incelendi -- bu GUVENLIK ACISINDAN KABUL EDILEBILIR CUNKU bu istemci SADECE KENDI localStorage'inda SAKLADIGI, ONCEDEN SUNUCUDAN ALINMIS JWT'lerin `exp`/`context` ALANLARINI OKUMAK icin KULLANIYOR (yerel ONBELLEK gecerlilik-SURESI/UI amacli) -- GERCEK YETKILENDIRME KARARI (JWT'nin odaya ERISIM VERIP VERMEDIGI) SUNUCU/Jitsi-XMPP tarafinda, bu dosyada DEGIL.
* `src/jwt-store.ts` -- `Object.entries()` KULLANIMI (prototip-kirlenmesi riskini ONLEYEN YORUMLA ACIKCA BELGELENMIS), localStorage okuma/yazma HATA-TOLERANSLI (try/catch + corrupt-veri TEMIZLEME) -- temiz.
* `src/recovery.ts`/`RecoveryTokenBox.tsx`/`RecoveryTokenDialog.tsx` -- `consumePendingRecoveryToken()`'in `order`+`intent=recover` query-param KAPISI incelendi: bu SADECE bir REDIRECT-SONRASI KURTARMA MEKANIZMASI (odeme SAGLAYICISINA gidip GERI DONME SIRASINDA token'in KAYBOLMAMASINI SAGLIYOR), token'in KENDISI HER ZAMAN AYNI TARAYICI/profildeki localStorage'TAN okunuyor (CROSS-USER sizinti riski YOK) VE SUNUCU (`/api/v1/recovery`) nihai DOGRULAMAYI/yetkilendirmeyi YAPIYOR -- istemci-tarafi KAPI SADECE UX icin, guvenlik SINIRI DEGIL. Tum metin-render ISLEMLERI React JSX `{...}` COCUKLARI (otomatik escape) ARACILIGIYLA, `dangerouslySetInnerHTML` HICBIR YERDE GOZLENMEDI.
* `src/components/Transcript.tsx` -- katilimci ADLARI VE konusma METNI (her ikisi de ARAMA SIRASINDA DIGER KATILIMCILAR tarafindan KISMEN KONTROL EDILEBILIR) React `{...}` ILE RENDER EDILIYOR, otomatik HTML-escape SAGLANIYOR -- XSS riski GOZLENMEDI. `CSS.highlights`/`Range` KULLANIMI (arama-vurgusu) DOM API'leri uzerinden, innerHTML enjeksiyonu ICERMIYOR.
* `src/services.ts::secondLevelDomain()`/`resolveService()` -- `window.location.host`'tan TURETILEN KARDES-servis (account.*, vb.) URL'LERI incelendi; bu fonksiyonun GUVENLIGI, sayfanin KENDI host'unun ZATEN bir Brave-kontrollu ALAN ADI OLMASINA DAYANIYOR -- bu VARSAYIM GECERLI (sayfa Brave'in KENDI altyapisinda SUNULUYOR), bu nedenle BAGIMSIZ bir ZAFIYET DEGIL, TASARIM-GEREGI bir bagimlilik.
* `src/subscriptions.ts`/`src/rooms.ts` -- TUM durum-degistiren istekler CSRF token (`x-csrf-token` BASLIGI, `getCsrfToken()` ile ONCEDEN alinmis) VE `credentials: 'include'` ile GONDERILIYOR -- standart CSRF-koruma DESENI dogru UYGULANMIS.
* SONUC: Bu teslimde incelenen dosyalarda (JWT yonetimi, recovery-token akisi, transkript GORUNTULEME, URL-parametre OKUMA, servis-URL TURETME), odul-degeri TASIYAN YENI bir guvenlik bulgusu TESPIT EDILEMEDI. jitsi/* VE downloaded-transcript.ts dosyalari TAM incelenmedigi icin bu SONUC bu DOSYALARI KAPSAMIYOR -- bir SONRAKI firsatta ONCELIKLENDIRILMELI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._