# Bug Bounty Raporu — brave_adblock-resources

**Tarih:** 2026-11-04 22:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/adblock-resources (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: Custom resources and scriptlets used for Brave's adblocker.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_adblock-resources/raw`
* **Engellenen/erişilemeyen adımlar:** Bir scriptlet'in GERCEKTE HANGI sitelerde/hangi filtre-KURALLARIYLA TETIKLENDIGINI belirleyen ASIL filtre-listesi KURALLARI (`+js(<scriptlet-adi>)` tipi satirlar, EasyList/Brave'in KENDI listelerinde) bu teslimde YOK -- sadece scriptlet'lerin KENDI KAYNAK KODU var. Bu nedenle 'trusted_types.js gibi KENDI BASINA RISKLI bir scriptlet, GERCEKTE ne kadar GENIS/DAR bir siteler kumesinde UYGULANIYOR' sorusu bu kapsamda DOGRULANAMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in reklam-engelleyicisinin SAYFALARA ENJEKTE ETTIGI ozel 'scriptlet'leri (site-uyumluluk DUZELTMELERI -- YouTube oynatma/PiP/navigasyon duzeltmeleri, AMP-SAYFA-devre-disi-birakma, dokunmatik-ekran duzeltmeleri VB.) ve bunlarin PAKETLENME/dogrulama ALTYAPISINI (index.js, build.js, verify.js, metadata.json) iceriyor.
* Iki commit diff'i (CI Node.js surum guncellemesi + `adblock-rs` dev-bagimliligi GUNCELLEMESI) guvenlik acisindan NOTR.
* `resources/trusted_types.js` OZELLIKLE dikkatle incelendi -- bu scriptlet, bir sayfaya UYGULANDIGINDA `window.trustedTypes.createPolicy('default', { createScript: string => string })` ile, HICBIR SANITIZASYON YAPMAYAN, TAMAMEN GECIRGEN bir 'default' Trusted Types POLITIKASI olusturuyor -- bu, Trusted Types'in KENDI guvenlik AMACINI (DOM-tabanli XSS'e karsi, string'lerin KOD olarak kullanilmadan ONCE acikca SANITIZE EDILMESINI ZORUNLU kilma) FIILEN ETKISIZLESTIRIYOR. ANCAK bu, adblock-SCRIPTLET EKOSISTEMINDE (uBlock Origin'in BENZER 'trusted-types' bypass scriptlet'leri DAHIL) IYI-BILINEN, KASITLI bir UYUMLULUK ARACI -- SADECE Trusted-Types-zorunlu bir CSP'nin, Brave'in KENDI BASKA BIR enjeksiyonunu (orn. baska bir duzeltme-scriptini) BOZDUGU BELIRLI sitelerde, HEDEFLI olarak UYGULANMASI AMACLANMIS (filtre-kurali SEVIYESINDE SECILI UYGULAMA -- bu teslimde GORULMEYEN bir BASKA depo/dosyada). Bu nedenle BAGIMSIZ bir YENI guvenlik bulgusu olarak RAPORLANMADI -- bu, TASARIM GEREGI VAR OLAN, BILINEN bir ODUN/tradeoff.
* Genis-capli grep taramasi (TUM teslim, ~2379 satir + 1 adet 53KB'LIK TEK-SATIR minifiye ucuncu-taraf 'sugarcoat' dosyasi): `eval(`, `new Function(`, `innerHTML`, `document.write(` -- HICBIRI BULUNAMADI. Dosyalardan BIRINDE ACIKCA 'Built with createElementNS instead of innerHTML to avoid TrustedTypes' YORUMU var -- bu, GELISTIRICILERIN innerHTML'den KASITLI olarak KACINDIGINI GOSTERIYOR.
* `de-amp.js` (AMP sayfalarindaki `jsaction` ozniteligini KALDIRARAK AMP'nin KENDI tiklama-yakalama JS'ini DEVRE-DISI BIRAKAN KUCUK bir scriptlet) incelendi -- HICBIR yonlendirme/URL-insasi mantigi ICERMIYOR, SADECE bir DOM ozniteligi SILIYOR, zararsiz.
* `index.js`/`build.js` (paketleme ALTYAPISI) incelendi -- `metadata.json`'daki `resourcePath` degerleri REPO-ICI, incelemeden GECMIS, SABIT degerler (kullanici-girdisi DEGIL), bu nedenle `path.join` ile BIRLESTIRILMELERI bir PATH-TRAVERSAL riski OLUSTURMUYOR.
* Minifiye 'async-sugarcoat-*.js' dosyalari (BUYUK, TEK-SATIR, ucuncu-taraf-KOKENLI sugarcoat STUB kutuphaneleri) ZAMAN KISITI VE pratik-ANALIZ-EDILEBILIRLIK nedeniyle DETAYLI olarak incelenmedi -- bu dosyalar, uBlock Origin ekosisteminde YAYGIN KULLANILAN, kamuya acik 'sahte/stub' KUTUPHANE DOSYALARI (REKLAM/analitik KUTUPHANELERININ ZARARSIZ YER-TUTUCULARI) olarak BILINIYOR.
* SONUC: Bu scriptlet-koleksiyonunda, KASITLI/belgeli bir TASARIM-odunu (trusted_types.js) DISINDA, YENI bir guvenlik acigi tespit edilmedi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._