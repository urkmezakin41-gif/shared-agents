# Bug Bounty Raporu — coinbase_mesh-sdk-go

**Tarih:** 2026-11-02 08:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/mesh-sdk-go, Go Mesh/Rosetta SDK - 'asserter' dogrulama paketi + API client).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_mesh-sdk-go/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; derlenip calistirilmadi., headerforwarder/forwarder.go ve keys/signer_secp256k1.go TAM dosyalari gelmedi, yalnizca son 2 commit'in DIFF'leri geldi; HEAD'deki tam hali bu diff'lerden cikarildi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* headerforwarder/forwarder.go (DIFF'TEN GORULEN, HEAD'DE ZATEN YAMALI): eski kod uc ayri sorun iceriyordu - (1) RLock-sonra-ayri-Lock deseni yaris durumuna acikti (concurrent node cagrilarinda header kaybi), (2) hf.incomingHeaders/outgoingHeaders map'leri hic temizlenmiyordu ('TODO: expire entries' yorumu) - uzun suren bir rosetta sunucusunda sinirsiz bellek birikimi (DoS potansiyeli), (3) RoundTrip caller'in *http.Request nesnesini KLONLAMADAN mutasyona ugratiyordu (Go http.RoundTripper sozlesmesini ihlal - es zamanli istekler arasinda header sizmasi/bozulmasi riski). UCU DE bu son commit'te duzeltildi: Lock boyunca tek kilitli erisim, handler donuste forget() ile temizlik, RoundTrip'te req.Clone(). HEAD'de acik kalan bir sey yok; bu nedenle rapor edilemez (zaten yamali).
* keys/signer_secp256k1.go (DIFF): BIP-340 Schnorr imzalama/dogrulama eklendi (btcec/v2 kutuphanesi kullanilarak); 32-byte mesaj hash uzunlugu kontrolu var, parse hatalari (ParsePubKey/ParseSignature) dogru sekilde error olarak donuyor - yeni kod da guvenli gorunuyor.
* asserter/block.go Amount(): big.Int.SetString(amount.Value, 10) ACIKCA base-10'a sabitlenmis (base 0 kullanilsaydi '0x..' hex veya '0...' octal olarak yorumlanabilirdi - bilinen bir zafiyet sinifi); bu kod bu tuzaga DUSMEMIS, dogru.
* asserter/account.go, asserter/utils.go: currency/amount tekillik kontrolleri, string/account array dogrulamalari (bos string, duplicate) tutarli ve saglam.
* client/api_call.go: io.ReadAll(response.Body) boyut siniri yok (buyuk Mesh node cevabinda bellek tuketimi) - ancak bu standart OpenAPI-uretilmis istemci kodu, SDK kullanicisi kendi secip baglandigi Mesh node'una karsi; saldirgan kontrolundeki bir ucuncu taraf degil (self-DoS sinifi, bounty disi).
* Genel: bu bir ISTEMCI SDK'si + dogrulama (asserter) kutuphanesi; en kritik dosyalarin (forwarder.go, signer_secp256k1.go) TAM hali gelmedi ama diff'ler HEAD'in zaten guvenli oldugunu gosteriyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._