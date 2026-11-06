# Bug Bounty Raporu — brave-intl_bat-go-solana-and-middleware

**Tarih:** 2026-11-01 22:45 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) - SOURCE_CODE wildcard https://github.com/brave/*, https://github.com/brave-intl/* (structured_scope id 943222, max_severity critical). Eksik dosyalar tamamlandi: libs/wallet/wallet.go, libs/middleware/*, services/wallet/keystore.go, services/skus/* (controllers/credentials/skus/vote/receipt/order/handler/cred).
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave-intl_bat-go-solana-and-middleware/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; Postgres/Kafka/Stripe/App Store/Play Store/Uphold entegrasyonlari calistirilmadi., services/skus/model, storage/repository tam kaynagi yok (bazi tur/limit fonksiyonlari dolayli okundu).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* ONCEKI TUR F2 (Solana linkleme kimlik dogrulamasiz hipotezi) KAPANDI: libs/wallet/wallet.go Info.LinkSolanaAddress -> isLinkReqValid iki imza ister: (1) Solana ed25519 imzasi (sunulan solana pubkey ile), (2) rewards cuzdan ed25519 imzasi (w.PublicKey - cuzdanin KENDI anahtari) uzerinden paymentID+nonce+solanaPubKey baglayan bir mesaj (solMsgParser, sabit zaman olmayan ama veri kamusal oldugu icin onemsiz bayt-bayt karsilastirma). Nonce bir CreateChallenge/chlRepo kaydindan gelir ve kullanildiktan sonra silinir (tek kullanimlik). Yani saldirgan kurbanin rewards cuzdan private key'i olmadan baska bir paymentID'ye kendi Solana adresini baglayamaz - hipotez gecersiz.
* Middleware (http_signed.go, simple_token.go, rate_limiter.go, request_host.go, digest.go) saglam: digest dogrulamasi govdeyi yeniden hesapliyor, tarih penceresi +-10dk, ED25519 + (request-target)+digest zorunlu headerlar, basit token sabit-zamanli karsilastirma (uzunluk sizintisi bilinen/kabul edilmis). request_host.go X-Forwarded-Host'u dogrudan Host basligina yaziyor (header-based host guveni) ama bu sadece loglama/imza host alani icin - yetkilendirme kararina girmiyor.
* services/skus: webhook imza dogrulamalari ayrik ve dogru goruluyor (Stripe: webhook.ConstructEvent HMAC; Play Store: gpsAuth.authenticate; Radom: radomAuth.Authenticate header; App Store: assnCertVrf sertifika zinciri - daha once incelendi, OID pinleme eklenmis). CreateOrderItemFromMacaroon: macaroon imzasi (decodeAndUnmarshalSku) olmadan caveat'lar GUVENILIR sayiliyor gibi gorunse de, mac.UnmarshalBinary + validateHardcodedSku (hardcoded SKU/macaroon anahtar listesi) once calisiyor - macaroon dogrulamasi (HMAC zinciri) kutuphanenin kendisinde; kaynagi gelmedi ama bu yol sadece Legacy/AC-Captcha icin ve 'MUST NOT be used for Premium' notu var.
* CreateOrderItemCredentials (credentials.go): odenmis siparis kontrolu (order.IsPaid()), item varligi, bos blindedCreds kontrolu, TLV2 icin istek-id/firstBCred esleme ile tekrar-gonderim tespiti (doCredentialsExist), parti limiti (checkTLV2BatchLimit), SingleUse/TLV2 icin miktar sinirlamasi (checkNumBlindedCreds) - hepsi mantikli ve bu turda okundu, aciklanan 'advisory lock yarisi' onceki surumde not edilmisti, mitigasyonlar yerinde.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._