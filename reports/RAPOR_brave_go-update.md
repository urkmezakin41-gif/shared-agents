# Bug Bounty Raporu — brave_go-update

**Tarih:** 2026-11-05 10:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/go-update (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Go. Description: Component update server for brave-core written in Go.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_go-update/raw`
* **Engellenen/erişilemeyen adımlar:** `batware.Metrics()` (github.com/brave-intl/bat-go/middleware) VE `server/middleware/cache.go`/`compress.go`'nun TAM icerigi (cache.go basligi GOZLEMLENDI ama DETAYLI incelenmedi) bu teslimde haric TUTULDU VEYA KISMEN gorundu -- `main.go`'daki port 9090 metrik DINLEYICISININ GERCEKTEN pprof/debug ROTALARINI DAHIL edip ETMEDIGI (batware paketi HARICI) DOGRULANAMADI. AYRICA, port 9090/6061'in GERCEK dagitimda (deployment) PUBLIC/private AG ERISIMININ NASIL YAPILANDIRILDIGI (AWS GUVENLIK GRUPLARI VB.) bu REPO'NUN KAPSAMI DISINDA, DOGRULANAMADI., `omaha/v4` paketindeki protocol/request/response dosyalari VE `server/middleware/cache.go`'nun TAM MANTIGI, ZAMAN KISITI nedeniyle v3 PAKETINE kiyasla DAHA AZ detayli incelendi (v3 ile BENZER YAPIDA OLDUKLARI GOZLEMLENDI AMA satir-SATIR KARSILASTIRMA YAPILMADI).

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki commit diff'i (controller.go'daki 'karisik-durum' REDIRECT MANTIGI DUZELTMESI, VE go.mod/go.sum'daki go-chi/chi BAGIMLILIK GUNCELLEMESI) -- ILKI zaten IYI-yonlu bir DAVRANIS-duzeltmesi (coklu BILINMEYEN extension'in HEPSININ dogru SEKILDE REDIRECT EDILMESI), IKINCISI rutin bagimlilik GUNCELLEMESI -- her ikisi de guvenlik acisindan NOTR/pozitif.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, TUM Brave tarayici ORNEKLERININ bilesen-GUNCELLEMELERI icin SORGULADIGI, DOGRUDAN INTERNETE ACIK (Omaha/update PROTOKOLU) SUNUCU -- bu nedenle critical severity ile TUTARLI VE EN YUKSEK-ONCELIKLI hedeflerden biri (GERCEK-ZAMANLI, GUVENILMEYEN GIRDI isleyen bir SUNUCU, dosya SISTEMI/paketleme SCRIPT'I DEGIL).
* `controller/controller.go` (TAM) incelendi -- redirect-HOST SECIMI (`GetUpdaterHostByType`) SADECE SABIT, ortam-DEGISKENINDEN (veya varsayilan SABIT) gelen UC host'tan (`componentupdater.brave.com`, `extensionupdater.brave.com`, `update.googleapis.com`) birini DONDUREN bir SWITCH -- client-SUPPLIED `@updater` DEGERI SADECE eslesen DALI SECMEK icin KULLANILIYOR, HOST'un KENDISINE ASLA ENTERPOLE EDILMIYOR. `RawQuery: r.URL.RawQuery` ICEREN redirect'ler UZERINDEKI `nosemgrep: open-redirect` BASTIRMASI bu nedenle DOGRU/GECERLI -- HOST SABIT OLDUGU icin bu GERCEK bir open-redirect DEGIL.
* `extension/extension.go::CompareVersions()` -- rastgele/bicimsiz (malformed) client-SUPPLIED versiyon STRING'LERINI (orn. harfler, bos PARCALAR) `strconv.Atoi` HATASINI SESSIZCE 0'a CEVIREREK GUVENLI SEKILDE isliyor; dizin SINIRLARI (indices) MATEMATIKSEL olarak HER ZAMAN GUVENLI (dongu SADECE DAHA KISA DIZININ uzunluguna KADAR ITERATE EDIYOR) -- panic/DoS riski GOZLENMEDI.
* `omaha/v3/request.go::UnmarshalXML()`/`UnmarshalJSON()` -- Go'nun STANDART `encoding/xml` kutuphanesi KULLANILIYOR, bu kutuphane TASARIM GEREGI DTD/harici-entity GENISLEMESINI DESTEKLEMIYOR -- XXE VE 'billion laughs' TURU entity-genisletme DoS SINIFLARI bu DIL/kutuphane SECIMI NEDENIYLE YAPISAL olarak MUMKUN DEGIL.
* `controller.go::UpdateExtensions()` -- istek govdesi `io.LimitReader` ile 10MiB'A SINIRLANDIRILMIS VE sinira ULASILDIGINDA ACIKCA reddediliyor -- asiri-buyuk-govde DoS'una karsi TEMEL bir KORUMA mevcut.
* `omaha/protocol/protocol.go::IsPingbackRequest()` -- JSON govdesinde HERHANGI bir DERINLIKTE 'events' ANAHTARININ varligini (NESTING SEVIYESINI AYIRT ETMEDEN) PINGBACK GOSTERGESI olarak KULLANIYOR -- ARASTIRILAN bir HIPOTEZ: bu, is-ici (nested) bir 'events' alani ICEREN MESRU bir update-check ISTEGININ YANLISLIKLA PINGBACK olarak SINIFLANDIRILIP (204 ile) GOZ ARDI EDILMESINE yol ACABILIR. ANCAK bu SADECE ISTEGI GONDERENIN KENDI isteginin ISLENMEMESI SONUCUNU DOGURUYOR (self-INFLICTED, BASKA bir kullaniciyi ETKILEMEYEN bir FONKSIYONEL-DOGRULUK SORUNU, guvenlik SINIRI ihlali DEGIL) -- bulgu olarak SUNULMADI.
* `server/server.go` -- `net/http/pprof` KOR-IMPORT'u VAR AMA `PPROF_ENABLED` ortam-DEGISKENI ile GATED, VARSAYILAN KAPALI, AYRI bir port'ta (6061) -- ana SUNUCU (8192, chi router) VEYA metrik SUNUCUSU (9090, batware.Metrics()) `http.DefaultServeMux`'U KULLANMIYOR, bu nedenle pprof VARSAYILAN dagitimda REACHABLE DEGIL. `batware.Metrics()`'in DAHILI ICERIGI bu teslimde YOK, TAM DOGRULANAMADI -- DUSUK-oncelikli bir BELIRSIZLIK olarak NOT EDILDI, BULGU olarak SUNULMADI (kod-DUZEYINDE GATING DOGRU UYGULANMIS).
* SONUC: Bu COK YUKSEK-DEGERLI, DIREKT internete ACIK sunucuda, incelenen EN KRITIK dosyalarda (istek-ayristirma, versiyon-karsilastirma, redirect-mantigi, boyut-sinirlamasi) odul-degeri TASIYAN YENI bir guvenlik bulgusu TESPIT EDILEMEDI -- kod TUTARLI olarak GUVENLIK-BILINCLI (Go'nun XXE-guvenli XML kutuphanesi, panic-guvenli versiyon-ayristirma, SABIT redirect-HOST'lari, boyut-SINIRLI istek govdesi).

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._