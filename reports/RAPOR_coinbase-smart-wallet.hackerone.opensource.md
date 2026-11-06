# Bug Bounty Raporu — coinbase-smart-wallet.hackerone.opensource

**Tarih:** 2026-11-01 01:06 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** confidence >= 90 ve verdict == PASS

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** Official HackerOne Open-Source (SOURCE_CODE) Bounty Program: Coinbase (https://hackerone.com/coinbase) - In-Scope Asset: https://github.com/coinbase/* (coinbase/smart-wallet). RAW proof JSON provided but asset_identifier mismatch noted below.
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase-smart-wallet.hackerone.opensource/raw`
* **Engellenen/erişilemeyen adımlar:** ONEMLI TUTARSIZLIK: Saglanan 'RAW HACKERONE API STRUCTURED_SCOPES JSON PROOF' kaydi asset_identifier olarak 'https://github.com/coinbase/cb-mpc' gosteriyor -- ama analiz edilen/talep edilen hedef 'coinbase/smart-wallet' ve 'base-org/contracts'. Kanit, analiz edilen hedefle EŞLEŞMİYOR. Bu kaydı asset-level yetki kanıtı olarak KULLANMADIM; yalnızca kodun kendisinin gercekligini (lisans basliklari, bilinen isimlendirme/mimari tutarliligi) bagimsiz olarak dogrulayarak ilerledim., StandardBridge.sol'un cagirdigi ICrossDomainMessenger'in gercek implementasyonu (replay/nonce koruma mantiginin asil yasadigi yer) bu pakette YOK; finalizeBridgeETH/finalizeBridgeERC20'nin cross-chain mesaj tekrar oynatmaya karsi tam korumasi bu dosyadan DOGRULANAMADI., ERC1271.sol, Receiver.sol, WebAuthn.sol, SignatureCheckerLib.sol, LibClone.sol gibi import edilen bagimliliklarin (Solady/webauthn-sol) kaynak kodlari saglanmadi; imza dogrulamasinin tam detaylari bu kutuphanelerin icinde.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* CoinbaseSmartWallet._authorizeUpgrade: 'onlyOwner' ile korunuyor, UUPS upgrade yetkisiz cagrilamiyor. validateUserOp icinde ayrica upgradeToAndCall hedefinin kod icerdigi kontrol ediliyor (bos/EOA adrese upgrade engelleniyor). Bu emirnamenin ozellikle vurguladigi 'upgradeTo() icin onlyOwner unutulmasi' sinifina girecek bir eksiklik YOK.
* MultiOwnable: addOwnerAddress/addOwnerPublicKey/removeOwnerAtIndex/removeLastOwner hepsi onlyOwner ile korunuyor. removeOwnerAtIndex son sahibi silmeyi engelliyor (LastOwner revert), removeLastOwner ise TERSI durumu zorunlu kiliyor (sadece tek sahip kaldiginda kullanilabilir) -- bu, 'hesabin sahipsiz kalmasi' riskine karsi mantikli bir ikili koruma.
* CoinbaseSmartWalletFactory.createAccount: owners.length == 0 kontrolu var, initialize() yalnizca ilk deploy'da cagriliyor (alreadyDeployed kontrolu ile), initialize() kendisi de nextOwnerIndex() != 0 ise revert ediyor (cift-initialize engellendi).
* executeWithoutChainIdValidation: yalnizca onlyEntryPoint, ve yalnizca canSkipChainIdValidation() whitelist'indeki selector'lere (owner yonetimi + upgrade) izin veriyor -- cross-chain replay edilebilir islemlerin kapsamini bilinçli ve dar tutuyor.
* StandardBridge: finalizeBridgeETH/finalizeBridgeERC20 onlyOtherBridge ile korunuyor (yalnizca dogru messenger'dan gelen cross-domain mesaj). ERC20 yolunda state guncellemesi (deposits azaltma) external transferden ONCE yapiliyor (dogru CEI sirasi). ETH yolunda ayri bir 'deposits' azaltmasi yok -- replay korumasi CrossDomainMessenger seviyesinde olmasi beklenir (bu pakette yok, dogrulanamadi).
* SONUC: Gercek, bilinen, denetlenmis Coinbase Smart Wallet + Base StandardBridge kodunda somut kanitli bir aciklik bulunmadi. Yukarida listelenen 3 eksik bagimlilik (CrossDomainMessenger, imza/webauthn kutuphaneleri) nedeniyle denetim TAM degil; ayrica 'proof' JSON'daki asset_identifier uyumsuzlugu ayri bir surec/veri butunlugu sorunu olarak kullaniciya bildirilmeli (bu benim bulgu degerlendirmemi etkilemedi, sadece scope kanitinin guvenilirligini dusurdu).

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥90 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._