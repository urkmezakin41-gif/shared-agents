# Bug Bounty Raporu — matomo-org_tracker-proxy

**Tarih:** 2026-11-01 14:05 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** confidence >= 90 ve verdict == PASS

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Matomo (https://hackerone.com/matomo) - SOURCE_CODE Asset Identifier: https://github.com/matomo-org/tracker-proxy (structured_scope id 1035630, eligible_for_bounty: true) - blok varlikla birebir eslesiyor. Siddet tablosu blokta yok. Program sayfasi bu ortamdan dogrulanamadi.
* **Ham veri kaynağı:** `scripts/bugbounty/out/matomo-org_tracker-proxy/raw`
* **Engellenen/erişilemeyen adımlar:** Program sayfasi bu ortamdan dogrulanamadi. Yalnizca halka acik kaynak kodun statik incelemesi; PHP calistirilmadi, hicbir sunucuya istek atilmadi., Okunan: piwik.php ve proxy.php (687 satir, tam). GELMEYEN: matomo-proxy.php / matomo.php (uc nokta dosyalari - $filerequest degiskeninin nereden ve nasil dogrulanarak geldigi), config.php.example, README. proxy.php'deki '.js' dosya yolu ($MATOMO_URL . $filerequest) SSRF/yol gecisi acisindan o dosyanin dogrulamasina baglidir; hukum verilemedi. Ayrica proxy'nin token_auth'u 'kendi yetkisiyle' enjekte etmesi Matomo CEKIRDEGINDE hangi parametrelerin kimlik dogrulama gerektirdigine (Tracker/Request.php) baglidir; cekirdek kodu gelmedi.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] IP SAHTECILIGI: getVisitIp() HTTP_X_FORWARDED_FOR/HTTP_CLIENT_IP/HTTP_CF_CONNECTING_IP basliklarini (tek gecerli IP ise) REMOTE_ADDR'den ONCE guveniyor ve bunu 'cip' olarak, proxy'nin token_auth'u ile yetkilendirerek Matomo'ya iletiyor. Guvenilir bir ters vekil olmadan herhangi bir istemci kendi ziyaretci IP'sini sahteleyebilir (analitik verisinin butunlugu, IP dislama filtrelerinin atlatilmasi). Projenin belgelenmis/eski davranisi; etki yalnizca analitik verisi -> odul disi/Informational.
* [ÖDÜL DEĞERİ YOK - ATLANDI] COOKIE ILETIMI: $COOKIE_ALLOWLIST tanimli degilse ziyaretcinin TUM Cookie basligi (site oturum cerezleri dahil) $MATOMO_URL'ye iletiliyor. Matomo ayri bir ucuncu tarafta (ör. bulut) barindiriliyorsa oturum cerezleri o tarafa sizar; yeni eklenen allowlist bunun icin hafifletme. Varsayilan fail-open. Sertlestirme onerisi, uzaktan istismar yolu yok -> odul disi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* TOKEN ENJEKSIYONU (cekirdek mantik, elle izlendi): Istemci token_auth, cip veya yetkilendirme gerektiren parametre ('cdt','cdo','country','region','city','lat','long') gondermemisse proxy kendi TOKEN_AUTH'unu ve ziyaretci IP'sini (cip) ekliyor; istemci herhangi birini gonderirse proxy token eklemiyor (istemci kendi yetkisiyle gider). Bos/dizi degerli token_auth/cip gonderimi ile proxy'nin degerini ezme girisimlerine karsi unset yapiliyor; $_GET ile $_POST birlesimi Matomo'nun (RequestSet) okudugu gibi degerlendiriliyor; PHP ad donusumu ('.'/bosluk -> '_') $_GET uzerinden ayni gorundugu icin tutarli. Toplu (bulk) JSON istekleri icin de ayni mantik (ust duzey token yalnizca TAMAMEN temiz bir toplu istekte, aksi halde yalniz temiz girislere girdi-basina token), sizma/ezme senaryolari kodda yorumlanmis ve ele alinmis.
* ACIK SORU (kanitlanamadi): Matomo cekirdeginde kimlik dogrulama gerektiren parametre listesi proxy'deki $overrideParams ('cdt','cdo','country','region','city','lat','long') + token_auth + cip ile birebir ayni olmak zorunda; eger cekirdekte baska bir parametre (ör. ziyaretci kimligini zorlayan 'cid') yalnizca yetkili istekte kabul ediliyorsa ve bu listede yoksa, proxy kendi yetkili token'ini bu parametreyi gonderen anonim isteklere de ekler ve ziyaretci kimligi/veri sahteciligine izin verir. Cekirdek (Tracker/Request.php) gelmedigi icin bunu NE DOGRULAYABILDIM NE ELEYEBILDIM; yalnizca eksik kanit olarak not ediliyor.
* BASLIK ENJEKSIYONU/CRLF: Accept-Language CR/LF/TAB'dan temizleniyor; user_agent PHP http/curl katmaninda CRLF'e karsi korunuyor ve istemcinin gonderebildigi bir UA'da zaten CRLF olamaz; Cookie basligi filtrelenen/ham istemci degeri; $http_ip_forward_header sabit yapilandirma + dogrulanmis IP. Enjeksiyon yolu gosterilemedi.
* YANIT ISLEME: sanitizeContent token'i (ham + URL-kodlu formlarda) '<token>' ile maskeliyor, MATOMO_URL/host'u PROXY_URL ile degistiriyor; forwardHeaders yalniz content-type, access-control-*, set-cookie basliklarini geciriyor. $PROXY_URL bu dosyada tanimli degil (config.php'den bekleniyor; tanimsizsa parse_url uyarisi). Yanit bolme/baslik enjeksiyonu: $httpStatus dogrudan header()'a veriliyor ama kaynagi guvenilir Matomo yanitidir.
* SONUC: Okunan dosyalarda yamasiz, kod kanitli bir zafiyet BULUNAMADI. Eksik: matomo-proxy.php ($filerequest dogrulamasi) ve Matomo cekirdeginin kimlik dogrulama gerektiren parametre listesi. 'Bulgu yok' yalnizca okunan dosyalar icin gecerlidir.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥90 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._