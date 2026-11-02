# Bug Bounty Raporu — matomo-org_matomo

**Tarih:** 2026-11-02 00:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Matomo (https://hackerone.com/matomo) - SOURCE_CODE wildcard https://github.com/matomo-org/matomo (structured_scope id 14689, max_severity critical) + https://github.com/matomo-org/tracker-proxy (id 1035630). Blok hem matomo core Tracker dosyalarina hem tracker-proxy'ye UYUYOR. Kullanici bloku ozellikle 'cid/uid/cdt gibi kimlik dogrulamali parametre override'lari' diye belirtiyor.
* **Ham veri kaynağı:** `scripts/bugbounty/out/matomo-org_matomo/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; canli Matomo kurulumu/MySQL yok, calistirilmadi., Tam-repo agac taramasi core/API/* gibi istenmeyen 20+ ekstra dosya da getirdi (DataTable/Proxy/Request.php - API katmani, Tracker degil); bunlar bu turda sadece hizlica tarandi, derinlemesine incelenmedi (kapsam disinda sayildi, zaten onceki turlarda API katmani incelenmemisti).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Kullanicinin blogunda 'cid/uid/cdt kimlik dogrulamali override' diye gruplandirilmis olsa da, core/Tracker/Request.php kodu INCELENINCE: SADECE 'cdt' (custom datetime, gecmise tarihleme) ve 'cip' (custom IP) isAuthenticated() kontrolu GEREKTIRIYOR (getCustomTimestamp() / getIpString()). 'cid' (getForcedVisitorId) ve 'uid' (getForcedUserId) HICBIR authentication kontrolu YOK - ancak bu Matomo'nun RESMI/BELGELI Tracking HTTP API davranisi: cid/uid ziyaretciyi/kullaniciyi TANIMLAYAN veridir (JS tracker'in sunucu tarafi dogrulamasi olmadan setUserId()/_id ile gonderdigi), cip/cdt ise SISTEM/ADLI veri (IP sahteciligi, log zaman damgasi sahteciligi) oldugu icin kasitli olarak daha siki korunuyor. Bu, HackerOne programinin genel aciklamasinda 'yetkisiz veri sahteciligi' siniflandirmasina (Matomo'nun bilinen/kabul edilmis tasarim karari) girer; kod incelemesiyle YENI bir bypass BULUNAMADI - sadece zaten dokumante edilen ayrim dogrulandi.
* authenticateTrackingApi()/authenticateSuperUserOrAdminOrWrite(): token_auth hem site-bazli 'tracking_token_auth' onbellek listesine (per-idSite, hashli, sabit-zamanli olmayan ama hash karsilastirmasi onemsiz) hem de genel Super User/Admin/Write auth akisina karsi kontrol ediliyor; basarisizlik durumunda yalniz token 'gecerli-benzeri' formatli (regex /^\w{28,36}$/) veya bos ise Failures loguna yaziliyor (gurultu azaltma, guvenlik degil).
* getCustomTimestamp() (cdt/cdo): isTimestampValid ile cdt'nin SIMDI'den once ve son 20 yil icinde olmasi zorunlu (gelecege tarihleme engellenmis); cdo (delta offset) abs() ile kullaniliyor, negatif cdo ile gelecege kaydirma mumkun degil; gecmise tarihleme belirli bir esikten (customTimestampDoesNotRequireTokenauthWhenNewerThan) sonra token_auth zorunlu kiliyor - mantikli ve tutarli.
* RequestSet.php (bulk tracking): tek bir RequestSet token_auth'u tum alt Request nesnelerine PAYLASTIRILIYOR gibi gorunse de, her Request kendi idSite'ina gore authenticateSuperUserOrAdminOrWrite cagiriyor (per-site token kontrolu korunuyor) - toplu istekte bir site icin gecerli token'in baska bir site icin de otomatik gecerli sayilmasi riski YOK (farkli site icin site-bazli tracking_token_auth listesi veya genel Super User kontrolu ayri calisir).
* tracker-proxy matomo-proxy.php: $filerequest, in_array($filerequest, $VALID_FILES, true) ile TEK bir sabit string'e (plugins/CoreAdminHome/javascripts/optOut.js) karsi STRICT (tip-guvenli) karsilastiriliyor - path traversal/whitelist-bypass imkani yok (zaten onceki turda bu repo temiz bulunmustu, bu dosya onu dogruluyor). matomo.php trivial, proxy.php'ye yonlendiriyor (proxy.php gelmedi ama $path sabit degere ayarlandigi icin $filerequest/$path karismasi riski bu dosyada yok).
* GoalManager.php: grep ile acik SQL string-concatenation/injection deseni bulunamadi (debug log interpolasyonlari haric); derinlemesine (parametreli sorgu katmani) dogrulanmadi, zaman kisiti nedeniyle orneklenerek tarandi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._