# Bug Bounty Raporu — brave-intl_bat-go

**Tarih:** 2026-11-01 20:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) - SOURCE_CODE wildcard https://github.com/brave/*, https://github.com/brave-intl/* (structured_scope id 943222, eligible_for_bounty: true, max_severity: critical; fork/archived haric). Blok varliga UYUYOR (brave-intl/bat-go). 'Critical odeniyor' iddiasi blokta var ama kopya/arsiv/fork durumu dogrulanamadi.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave-intl_bat-go/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; calistirilmadi (Postgres, Uphold, Solana, reputation servisi yok)., Eksik dosyalar: libs/middleware (HTTPSignedOnly, GetKeyID, BearerToken, RateLimiter, HostTransfer), libs/wallet/wallet.go (Info.LinkSolanaAddress - Solana mesaj formati paymentID/nonce'a bagli mi?), services/wallet/keystore (DecodeEd25519Keystore ve LookupVerifier), services/skus/*.go tam kaynak, libs/digest., Repo icindeki docs/*.md 'cozulmus rapor' iddialari bagimsiz dogrulandi; metne guvenilmedi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Temiz/sağlam bulunanlar: httpsignature (digest govdeden yeniden hesaplaniyor, sunucu algoritma+header listesini zorluyor, Ed25519 stdlib, HMAC sabit-zamanli), Uphold decodeTransaction (digest + imza + remarshal birebir esitlik, sinirli hedef dogrulamasi), Uphold claim/connect rotasi HTTP imzasiz ama islem cuzdan anahtariyla imzali oldugu icin guvenli, LinkWallet/ConnectCustodialWallet advisory lock + slot sayimi ayni linking_id uzerinde serilestirilmis, SQL parametreli, v3 GET rotalari ham kaynakta hala kayitli ancak dokuman/kapsam geregi kaldirilma yolunda.
* Kucuk kod kokusu (guvenlik degil): LinkUpholdWallet ErrInvalidCountry dalinda userID bos iken HasPriorLinking cagriliyor ve hata kontrolu priorLinkingErr yerine err'e bakiyor (fail-closed). BuildSigningString Host dali X-Forwarded-Host varken req.Header['Host']'a dusuyor (genelde bos) - imza host'a baglanmayabilir, ancak yalniz imzali header listesinde 'host' varsa gecerli; cuzdan imzalari digest+(request-target) kullanıyor.
* Dokuman (SECURITY.md / docs) iddiasi 'paymentID rastgele UUIDv4' - CreateRewardsWallet v4 paymentID'yi uuid.NewV5(ClaimNamespace, publicKey) ile turetiyor (v3 NewV4). Public key bilen paymentID'yi hesaplayabilir; public key ise sunucu disinda yayinlanmiyor, bu yuzden pratik etki yok.
* Son commit'ler (SKUs quantity<1, receipt advisory lock, App Store x5c OID dogrulamasi) zaten yamali; HEAD'de acik kalan sinif gorulmedi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 2 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 20 | REJECT | paymentID bilgisi gerekir, donen veri harcama yetkisi vermez; program bu sinifi N/A sayiyor. |
| F2 | 15 | REJECT | Dogrulayici kod (libs/wallet/wallet.go) teslim edilmedi; yalnizca hipotez, kanit yok. |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._