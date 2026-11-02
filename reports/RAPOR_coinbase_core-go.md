# Bug Bounty Raporu — coinbase_core-go

**Tarih:** 2026-11-02 22:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/core-go - prime-sdk-go'nun bagimli oldugu paylasilan HTTP/WebSocket cekirdek kutuphanesi, onceki turda eksik bagimlilik olarak not edilmisti, bu turda geldi).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_core-go/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* http.go::makeCall(): headersFunc (imzalama) TAM OLARAK govde (requestBody=json.Marshal(request) sonucu) HAZIRLANDIKTAN SONRA ve HTTP cagrisi YAPILMADAN ONCE cagriliyor - imza ile gonderilen govde arasinda TAHRIFAT PENCERESI yok (TOCTOU riski yok).
* DIKKAT CEKICI AMA ZAFIYET OLMAYAN NOKTA: imzalama fonksiyonuna 'parsedUrl.Path' (sorgu dizesi HARIC) geciliyor, ama GERCEK HTTP istegi 'callUrl' (sorgu dizesi DAHIL: baseUrl+path+query) ile yapiliyor. Yani HMAC imzasi sorgu parametrelerini KAPSAMIYOR. Bu, Coinbase'in COK ESKI/belgelenmis CB-ACCESS-SIGN tasarim deseniyle (Prime/Exchange/Advanced Trade API'lerinde yillardir ayni sema: timestamp+method+requestPath+body, sorgu dizesi HARIC) TUTARLI - sunucu tarafi da AYNI sekilde dogruluyor olmali (asimetri yok), ve GET istekleri icin sorgu parametreleri tipik olarak filtre/sayfalama (fon hareketi degil); POST/PUT/PATCH'te gercek hassas veri (adres/tutar) GOVDEDE, sorgu dizesinde degil. Bu nedenle YENI bir guvenlik acigi degil, bilinen/kasitli bir API-imza semasi; yine de HackerOne'a kendi programinin bu semayi (dokumante edilmisse) nasil tanimladigini CHECK etmek faydali olabilir.
* DefaultHttpClient(): ResponseHeaderTimeout/DialContext.Timeout/TLSHandshakeTimeout hepsi makul sinirlar icinde ayarli (DoS/askida-kalma onleme); InsecureSkipVerify HICBIR YERDE kullanilmiyor (varsayilan TLS sertifika dogrulamasi aktif).
* ws.go/DialWebSocket: TLSClientConfig cagiran taraftan geliyor, varsayilan (nil) durumda gorilla/websocket'in kendi guvenli varsayilanlarini kullaniyor; InsecureSkipVerify sabit-kodlu DEGIL.
* Bu paket, prime-sdk-go incelemesinde 'eksik bagimlilik' olarak not edilen core-go'nun TAM KARSILIGI; HMAC imzalama akisinin zamanlamasi/govde butunlugu dogrulandi, aciklanan tasarim onceki turun varsayimlariyla TUTARLI cikti.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._