# Bug Bounty Raporu — coinbase_smart-wallet

**Tarih:** 2026-11-03 02:44 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/coinbase/* -> https://github.com/coinbase/smart-wallet (structured_scope id: 1028888, eligible_for_bounty: true, max_severity: critical). Language: Solidity. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_smart-wallet/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Coinbase'in ERC-4337 akilli hesap cuzdani (coinbase/smart-wallet) - fon saklama acisindan en yuksek onem derecesine sahip Coinbase hedeflerinden biri. Teslim edilen son commit diff'leri (a4e83fd36c, d0c113e7ba) yalnizca Makefile ve remappings.txt degisiklikleri icerir; sozlesme mantiginda degisiklik yok.
* Dort cekirdek sozlesme (CoinbaseSmartWallet.sol, MultiOwnable.sol, ERC1271.sol, CoinbaseSmartWalletFactory.sol) ile ERC1271InputGenerator.sol, DeployFactory.s.sol ve Certora harness/mock dosyalari (test-amacli, production'da deploy edilmiyor) tam olarak okundu.
* MultiOwnable.sol: addOwnerAddress/addOwnerPublicKey/removeOwnerAtIndex/removeLastOwner fonksiyonlari onlyOwner modifier'i ile korunuyor; _checkOwner() msg.sender'in kayitli bir owner VEYA address(this) olmasini sart koyuyor. Owner degisikligi ancak (a) dogrudan bir owner imzasiyla ERC-4337 UserOperation uzerinden EntryPoint araciligiyla, veya (b) sozlesmenin kendisi (self-call, yani zaten dogrulanmis bir UserOperation'in execute/executeBatch/executeWithoutChainIdValidation cagrisi) tarafindan yapilabilir. Yetkisiz owner ekleme/cikarma yolu bulunamadi.
* CoinbaseSmartWallet.validateUserOp: REPLAYABLE_NONCE_KEY (8453) kontrolu dogru uygulanmis -- executeWithoutChainIdValidation CAGRILIYORSA nonce key'in bu deger olmasi, CAGRILMIYORSA bu degerden FARKLI olmasi zorunlu tutuluyor (iki yonlu kontrol, bypass yolu yok). canSkipChainIdValidation() whitelist'i (addOwnerPublicKey, addOwnerAddress, removeOwnerAtIndex, removeLastOwner, upgradeToAndCall) kasitli bir tasarim: owner senkronizasyonunun zincirler-arasi replay edilebilmesini saglar; upgradeToAndCall icin ayrica batch icinde kod uzunlugu sifir olan (codeless) bir implementation'a yukseltme girisimi InvalidImplementation ile reddediliyor -- bu, gecmiste bilinen bir 'cross-chain replay ile hesabi codesiz implementation'a yukseltip kilitleme' sinifi riskine karsi aktif bir savunma.
* ERC1271.sol (replaySafeHash / isValidSignature): domain ayirici {name:'Coinbase Smart Wallet', version:'1', chainId, verifyingContract=address(this)} ve typehash CoinbaseSmartWalletMessage(bytes32 hash) -- bu, coinbase_cdp-sdk'nin python/cdp/actions/evm/sign_and_wrap_typed_data_for_smart_account.py dosyasinda istemci tarafinda varsayilan EIP-712 domain/typehash degerleriyle TAM ORTUSUYOR. SignatureWrapper{ownerIndex, signatureData} ABI kodlamasi da istemci tarafindaki sarmalama ile ayni. Istemci-zincir uyumsuzlugu BULUNAMADI; onceki oturumdan tasinan hipotez guvenli olarak kapatildi.
* _isValidSignature: ownerBytes.length==32 ise adres+ECDSA (SignatureCheckerLib.isValidSignatureNow, EIP-1271/6492 uyumlu akilli sozlesme imzalarini da destekler), ==64 ise WebAuthn (secp256r1) public key + WebAuthn.verify. Gecersiz uzunlukta InvalidOwnerBytesLength ile revert. Mantikta acik bulunamadi.
* CoinbaseSmartWalletFactory: createAccount() deterministik CREATE2 (LibClone.createDeterministicERC1967), owners.length==0 ise OwnerRequired ile revert, zaten deploy edilmisse initialize() tekrar cagrilmiyor (MultiOwnable._initializeOwners zaten nextOwnerIndex()!=0 kontrolu ile ikinci init'i reddediyor -- cift koruma). Salt = keccak256(abi.encode(owners, nonce)) -- front-running ile adres cakismasi/ele gecirme riski yok (CREATE2 adresi owners'a baglidir, saldirganin ayni owners ile hesabi 'claim' etmesi onceden deploy edeni etkilemez).
* ERC1271InputGenerator.sol: production'da deploy edilmiyor, yalnizca eth_call simulasyonu icin -- ERC-6492 standardina uygun, 'constructor icinde return' paternini kasitli kullaniyor; guvenlik acisindan calistirma-zamani riski yok (asla zincire deploy edilmiyor).
* Certora harness/mock dosyalari (CoinbaseSmartWalletHarness.sol, EntryPointMock.sol) formal verification test altyapisi -- production kapsami disinda, inceleme amaciyla okundu ancak bulgu kaynagi olarak degerlendirilmedi.
* SONUC: Bu oturumda teslim edilen veri (yalnizca trivial build-tooling diff'leri + tam kaynak kod statik incelemesi) icinde yeni, PASS seviyesinde veya hint-tier seviyesinde raporlanabilir bir güvenlik acigi TESPIT EDILEMEDI. Sozlesmeler, istemci SDK'nin varsaydigi imza/replay-safe-hash semasiyla tam uyumlu ve bilinen replay/upgrade risklerine karsi aktif korumalar iceriyor. Temiz rapor (findings=[]) teslim ediliyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._