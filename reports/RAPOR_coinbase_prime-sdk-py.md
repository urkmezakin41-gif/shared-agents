# Bug Bounty Raporu — coinbase_prime-sdk-py

**Tarih:** 2026-11-02 23:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/prime-sdk-py, Coinbase Prime REST API icin Python istemci SDK'si).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_prime-sdk-py/raw`
* **Engellenen/erişilemeyen adımlar:** Dosyalarin cogu otomatik-uretilmis ince servis sarmalayicilari (services/*/*.py) ve apiSpec/ kod-uretim script'leri - orneklenerek tarandi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* client.py::generate_headers/sign: HMAC-SHA256 (timestamp+method+path+body), prime-sdk-ts ve prime-sdk-go ile AYNI semaya tam uyumlu. CB-ACCESS-SIGN semasinda (bu SDK ailesinde) hic 'nonce' alani yok - bu yuzden diger Coinbase SDK'larinda (cdp-sdk Python, coinbase-sdk-nodejs) bulunan 'nonce icin CSPRNG kullanilmiyor' sinifi sorun BURADA UYGULANAMAZ (ilgisiz).
* request(): imzalama icin json.dumps(body) kullaniliyor, GERCEK istek icin requests kutuphanesinin kendi json= parametresi (ayni json.dumps semantigi) kullaniliyor - iki serilestirme arasinda bir TUTARSIZLIK OLSAYDI her imzali istek HATA verirdi (production'da calisan bir SDK oldugu icin bu zaten dogrulanmis).
* credentials.py: Credentials.from_env/from_json sadece JSON parse + zorunlu alan kontrolu; secret deger loglanmiyor.
* base_response.py: dataclass tabanli deserileştirme (safe_instantiate), eval/pickle/unsafe reflection yok.
* Bu SDK, ayni ailenin (prime-sdk-ts, prime-sdk-go, core-go) ONCEKI turlarda TEMIZ bulunan esdegerleriyle AYNI kalite ve tasarim desenini tasiyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._