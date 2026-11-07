# Bug Bounty Raporu — brave_brave-search-extension

**Tarih:** 2026-11-07 23:38 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/brave-search-extension (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_brave-search-extension/raw`
* **Engellenen/erişilemeyen adımlar:** `src/manifest.jsonc`'in TAM icerigi (izinler, content_scripts, background SERVICE-worker TANIMLARI) bu teslimde YER ALMIYOR (SADECE bir commit diff'inde KUCUK bir METADATA DEGISIKLIGI goruluyor) -- eklentinin TAM izin-KAPSAMI (orn. `<all_urls>` content-script ENJEKSIYONU VAR MI, YOK MU) DOGRUDAN DOGRULANAMADI. ANCAK README'nin 'Configures Brave Search as the default search engine' ACIKLAMASI VE teslim edilen TUM kaynak dosyalarinin (SADECE eklentinin KENDI New Tab SAYFASI icin) OLMASI, bunun BASKA sitelere ENJEKTE EDILEN bir content-script ICERMEDIGINI GUCLU sekilde ima EDIYOR., `/build` dizinindeki paketleme SCRIPT'LERI (README'de BAHSEDILEN) bu teslimde YER ALMIYOR -- build-zamani ARAC GUVENLIGI DEGERLENDIRILEMEDI (ANCAK bu runtime saldiri-YUZEYI DISINDA kalir).

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i (npm bagimlilik GUNCELLEMESI VE manifest.jsonc'de KUCUK bir METADATA/surum-ENJEKSIYONU DUZENLEMESI) -- kod-MANTIGI degisikligi icermiyor, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Search'u VARSAYILAN arama MOTORU olarak YAPILANDIRAN VE bir 'New Tab' sayfasi SUNAN, Chrome/Firefox/Edge'de DAGITILAN KUCUK bir tarayici EKLENTISI.
* TUM bilesenler (ask-ai, context-menu, cta, download, search, preferences) TEK TEK incelendi -- HER BIRINDEKI `shadowRoot.innerHTML =` atamalarinin TAMAMEN SABIT/statik SABLON-dizgileri (TEMPLATE LITERAL) OLDUGUNU, HICBIR YERDE DINAMIK/DIS kaynakli VERININ (kullanici girdisi, AG-yaniti, chrome.i18n MESAJLARI DAHIL) DOGRUDAN HTML'E ENJEKTE EDILMEDIGINI SATIR SATIR DOGRULADIM -- `replaceDataI18nAttributes()` SADECE `el.textContent` (metin, HTML PARSE EDILMEZ) VEYA `el.setAttribute()` (OZNITELIK, KOD YURUTMEZ) KULLANIYOR, ASLA `innerHTML` ILE DEGIL.
* src/newtab/components/search/index.js -- kullanicinin arama SORGUSU (`input[name='q']`) SADECE `URLSearchParams` ile DOGRU sekilde KODLANARAK bir URL'E EKLENIYOR (Ask AI yonlendirmesi icin) -- HTML'E ASLA YAZILMIYOR, injection riski YOK.
* src/newtab/components/preferences.js -- TERCIHLER `localStorage` (eklentinin KENDI, SABIT origin'INDE) ile SAKLANIYOR -- BASKA bir siteden ERISILEMEZ, BU bir content-script DEGIL bir KENDI-SAYFASI (own-page) eklentisi oldugu icin CROSS-ORIGIN bir sizinti/MANIPULASYON riski YOK.
* SONUC: Bu, cok KUCUK, kendi-ICERIGINE (self-contained) sahip, SADECE statik SABLON KULLANAN bir New-Tab-degistirme eklentisi -- dinamik HTML enjeksiyonu, mesaj-GECIS GUVENLIGI veya CROSS-origin veri-akisi gibi TIPIK eklenti-guvenlik RISK alanlari ICERMIYOR. Odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI, rapor TEMIZ olarak dispatch edilmeli.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._