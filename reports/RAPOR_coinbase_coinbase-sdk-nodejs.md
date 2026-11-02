# Bug Bounty Raporu — coinbase_coinbase-sdk-nodejs

**Tarih:** 2026-11-02 20:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/coinbase-sdk-nodejs, TypeScript istemci SDK'si - cuzdan/transfer/trade/staking/kontrat cagirma).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_coinbase-sdk-nodejs/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; CDP API'sine karsi calistirilmadi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* createTransfer/createTrade/validateCanTrade/getDestinationAddressAndNetwork (wallet_address.ts, en buyuk dosya, 40KB): bakiye kontrolu (currentBalance.lessThan), ag eslesmesi (destination.getNetworkId() !== this.getNetworkId()), signer/private-key varligi kontrolu (Coinbase.useServerSigner && !this.key) hepsi tutarli ve mantikli; private key yalniz yerel imzalama icin (ethers.Wallet) kullaniliyor, disariya sizdirilmiyor.
* buildJWT/buildECJWT/buildEdwardsJWT: EC (ES256) ve Ed25519 anahtar turleri dogru ayirt ediliyor, exp=now+60 (kisa omurlu), aud/iss/sub claim'leri dogru. extractPemKey yalniz '-----BEGIN EC PRIVATE KEY-----' + footer iceren string'leri kabul ediyor (basit ama yeterli format kontrolu).
* Private key/secret loglanmasi: authenticator.ts ve wallet_address.ts'de kontrol edildi, gizli degerleri loglayan bir console.log/print cagrisi bulunamadi (yalniz debug modunda method+URL loglaniyor, kimlik bilgisi degil).

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 20 | REJECT | Nonce acik metin ve imza icin kritik degil; CDP backend'inin anti-replay davranisi bilinmeden etki dogrulanamaz. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._