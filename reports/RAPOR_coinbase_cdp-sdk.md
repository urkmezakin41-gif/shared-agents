# Bug Bounty Raporu — coinbase_cdp-sdk

**Tarih:** 2026-11-02 12:53 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/cdp-sdk, EVM/Solana cuzdan istemci kutuphanesi - Python + Go, JWT auth, spend permissions, smart account imzalama, swap/transfer).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_cdp-sdk/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; CDP API'sine karsi calistirilmadi., cdp.spend_permissions (__init__.py, ABI tanimlari), evm_accounts/send_transaction'in alt katmanlari, ve openapi_client model siniflari tam olarak gelmedi (sadece bazi tuketicileri geldi).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* generate_wallet_jwt() (ayni dosyada) dogru sekilde uuid.uuid4() (CPython'da os.urandom destekli, guvenli) kullaniyor - bu da _generate_nonce()'daki random.choices kullaniminin TUTARSIZ bir gozden kacirma oldugunu guclendiriyor.
* sign_and_wrap_typed_data_for_smart_account.py: Coinbase Smart Wallet'in replay-safe hash + SignatureWrapper semasi (domain='Coinbase Smart Wallet', chainId+verifyingContract=smart account adresi ile baglanmis, ownerIndex+signatureData ABI-encode) DOGRU ve TAM uygulanmis - zincirler/hesaplar arasi imza tekrar kullanimini onluyor, bilinen on-chain sozlesme semasiyla eslesiyor.
* spend_permissions/account_use.py ve smart_account_use.py: istemci tarafinda 'value <= allowance' kontrolu YOK (docstring bunu varsayiyor) ama bu sorun degil - gercek yetki kontrolu SpendPermissionManager on-chain sozlesmesinde (bu depoda degil) yapiliyor; istemci sadece cagriyi kodluyor, asiri deger zaten zincirde revert eder.
* JWT claim yapisi (generate_jwt): 'uris' claim'i REST istekleri icin dogru olusturuluyor (method+netloc+path), websocket icin atlaniyor; nbf/exp dogru sekilde ayarlaniyor (varsayilan 120sn). _parse_private_key hem PEM EC hem base64 Ed25519 anahtarlarini guvenli bir sekilde ayirt ediyor.
* Secrets/API key loglanmasi: grep ile jwt.py/api_clients.py/cdp_client.py icinde secret/key/token icerebilecek print/logger cagrisi bulunamadi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 20 | REJECT | Nonce tahmini basli basina gecerli imza uretmiyor; somut bir guvenlik atlamasi gosterilemedi. | CDP backend'in JWT dogrulama/anti-replay mantigi (bu depoda degil, Coinbase'in sunucu tarafi kodu) |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._