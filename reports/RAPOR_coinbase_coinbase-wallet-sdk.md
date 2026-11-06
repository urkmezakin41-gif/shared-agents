# Bug Bounty Raporu — coinbase_coinbase-wallet-sdk

**Tarih:** 2026-11-02 09:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/coinbase-wallet-sdk, dApp<->wallet popup/postMessage protokolu, TypeScript).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_coinbase-wallet-sdk/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; tarayicida calistirilmadi., EN KRITIK dosya GELMEDI: packages/wallet-sdk/src/util/cipher.ts (generateKeyPair, deriveSharedSecret, encryptContent/decryptContent - ECDH P-256 + AES-GCM gercek implementasyonu, IV/nonce uretimi). Bu olmadan nonce tekrar kullanimi/IV uretimi gibi kritik kripto hatalari DOGRULANAMADI., apiSpec/util/web.ts (openPopup/closePopup), store/migrations.ts, ve namespaces/solana/codec.ts gibi yardimci dosyalar da gelmedi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Communicator.ts (postMessage katmani): onMessage listener'i event.origin'i KEYS POPUP'IN KENDI origin'ine (this.url.origin, varsayilan CB_KEYS_URL=keys.coinbase.com) karsi sikica kontrol ediyor - postMessage spoofing/origin karistirma riski yok.
* KeyManager.ts + encrypt.ts/decrypt.ts: ECDH P-256 (Web Crypto CryptoKey) + AES-GCM paylasilan sir tasarimi standart; sir yoksa 'unauthorized' hatasi firlatiliyor (sessiz basarisizlik yok). setPeerPublicKey eski paylasilan sirri gecersiz kiliyor (sharedSecret = null). Gercek nonce/IV uretim mantigi util/cipher.ts'de (gelmedi).
* handshake.ts/post.ts/send.ts: handshake acik metin anahtar degisimi + wallet'in ilk sifreli cevabini cozme akisi tasarim olarak klasik ECDH; MITM korumasi TLS'e (keys.coinbase.com) ve ayni-origin postMessage kisitlamasina dayaniyor - bu SDK kodu katmaninda baska bir tasarim acigi yok.
* isCoinbaseWalletHost.ts: kendi dokumantasyonunda ACIKCA 'bu sinyaller sadece yonlendirme ipucu, guven siniri OLARAK KULLANILMAMALI' diye uyariyor. connect.ts'teki tek kullanimini dogruladim: true donerse yalniz window.ethereum/wallet-standard injected provider'a delege ediyor (ayni-origin, zaten dapp'in dogal guven modeli) - sifreleme/anahtar yonetimi akisina GIRMIYOR. Dokuman-vs-kullanim uyumsuzlugu yok.
* session/grants.ts (activeGrantForChain/assertInvokeAuthorized/sessionCovers): istemci tarafi bir onbellek/kisayol mantigi; gercek yetkilendirme cuzdan backend'inde (bu depoda degil). Istemci tarafindaki bir bypass en fazla UX hatasi yaratir, guvenlik atlamasi degil (cuzdan kendi yetkilendirmesini tekrar dogrulamali).
* parseCaip27.ts: dapp'in GIDEN wallet_invokeMethod cagrisini sikica dogruluyor (chainId formatini, method'un wallet_connect/wallet_createSession/wallet_invokeMethod'u ic ice gecirmesini engelliyor).
* store/store.ts: ECDH oturum anahtar ciftini (kullanicinin GERCEK cuzdan anahtari DEGIL, yalniz postMessage kanalini sifrelemek icin) localStorage'da JSON olarak tutuyor - bu SDK sinifi icin standart/kabul edilen tasarim (XSS zaten her seyi ele gecirir, storage mekanizmasi fark etmez).

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._