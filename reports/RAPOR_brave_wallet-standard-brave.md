# Bug Bounty Raporu — brave_wallet-standard-brave

**Tarih:** 2026-11-04 20:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/wallet-standard-brave (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_wallet-standard-brave/raw`
* **Engellenen/erişilemeyen adımlar:** `src/window.ts` SADECE bir TYPESCRIPT ARAYUZ (interface) tanimi -- GERCEK `BraveWallet` implementasyonu (yani `window.braveSolana`'nin KENDISI, kullanici-onayi/imzalama UI'si DAHIL TUM native kopru kodu) brave-core (veya baska bir Brave deposu) icinde, BU TESLIMDE DEGIL. Bu nedenle 'kullanici-onayi GERCEKTEN her imzalama/baglanma isteminde ZORUNLU mu' sorusunun KENDISI bu teslim kapsaminda DOGRULANAMAZ -- bu repo SADECE var-olan bir providera INCE bir UYARLAMA (adapter) katmani.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Wallet'in Solana destegini, DAPP'lerin (web3 web siteleri) KULLANDIGI standart 'Wallet Standard' arayuzune UYARLAYAN KUCUK bir TypeScript paketi. `src/register.ts`, `src/solana.ts`, `src/util.ts` ACIKCA 'copied from @wallet-standard/wallet' / '@solana/wallet-standard-chains' olarak ISARETLENMIS -- bunlar BRAVE'E OZGU kod DEGIL, ekosistem-standardi REFERANS implementasyonu. BRAVE'E OZGU mantik SADECE `src/wallet.ts` (`BraveWalletWallet` sinifi), `src/account.ts`, `src/initialize.ts`, `src/window.ts` (ARAYUZ) dosyalarinda.
* Iki commit diff'i, AYNI `package-lock.json` BAGIMLILIK-GUNCELLEMESI (SADECE DEV bagimliliklar -- rollup/shx build-araclari) olarak GORUNUYOR -- calisma-zamani (runtime) KODUNU ETKILEMIYOR, guvenlik acisindan NOTR.
* `src/wallet.ts`'teki `BraveWalletWallet` sinifinin TUM imzalama metotlari (`#signAndSendTransaction`, `#signTransaction`, `#signMessage`) OZELLIKLE dikkatle incelendi: HER BIRI, cagiranin GECIRDIGI `account` nesnesinin, SAKLANAN `this.#account` ile REFERANS-ESITLIGI (`!==`) tasimasini ZORUNLU KILIYOR ('invalid account' hatasi) -- bu, bir dApp'in SAHTE/baska bir hesap NESNESI gecirip BASKA bir hesaba BAGLI islemleri IMZALATMASINI ONLUYOR. `isSolanaChain(chain)` ile zincir-kimligi de DOGRULANIYOR. TUM gercek imzalama/gonderme ISLEMLERI, `this.#braveWallet.signAndSendTransaction/signTransaction/signAllTransactions/signMessage` araciligiyla VAR-OLAN native-koprulu metotlara DELEGE EDILIYOR -- bu adapter KENDI BASINA HICBIR imzalama mantigi UYGULAMIYOR, HICBIR onay-adimini ATLAMIYOR/KISA-DEVRE YAPMIYOR; SADECE girdi-dogrulamasi EKLIYOR.
* `src/account.ts`'teki `BraveWalletWalletAccount` sinifinin `publicKey`/`chains`/`features` GETTER'LARI, ic DIZILERIN KENDISINI DEGIL, `.slice()` ile SAVUNMACI bir KOPYASINI DONDURUYOR -- dis kodun (bir dApp'in) DONEN bir diziyi MUTATE ederek ic durumu BOZMASI (orn. `account.publicKey[0] = 0` gibi bir girisimin SESSIZCE basarisiz OLMASI, cunku kopya uzerinde calisir) ENGELLENIYOR -- IYI bir savunmaci-programlama ORNEGI.
* SONUC: Bu KUCUK uyarlama-katmaninda HICBIR guvenlik acigi tespit edilmedi. Asil guvenlik-kritik mantik (kullanici-onayi UI'si, native imzalama) bu reponun KAPSAMI DISINDA.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._