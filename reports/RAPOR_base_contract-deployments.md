# Bug Bounty Raporu — base_contract-deployments

**Tarih:** 2026-11-01 23:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/base/* (structured_scope id 1028889, max_severity critical). Blok varliga UYUYOR (base/contract-deployments: standby/active/archive upgrade task script'leri + Python orkestrasyon araclari).
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_contract-deployments/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; forge/foundry ile derleme veya simulasyon yapilmadi (Foundry/forge-std, @base-contracts, nitro-validator bagimliliklari gelmedi)., Denim upgrade'in en buyuk script'i (ExecuteDenimUpgradeWithAllL2Predeploys.s.sol, ~39KB) satir satir degil, orneklenerek incelendi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Python orkestrasyon araclari (new-task.py, standby-task.py, task-status.py): subprocess COK LISTE FORMUNDA cagriliyor (shell=True yok), kullanici girdisi IDENTIFIER regex'i (^[a-z][a-z0-9]*(-[a-z0-9]+)*$) ile kisitlaniyor, tarih ISO formati dogrulaniyor, dosya yollari repo koku altinda sabit desenlerle insa ediliyor (path traversal yuzeyi yok). standby-task.py archive(): git show/ls-tree ile origin/main karsilastirmasi, dosya icerik hash karsilastirmasi, sembolik link reddi (path.is_symlink() -> ValueError) - saglam.
* DelayUpgradeActivation.s.sol (standby - acil senaryo): on-check+son-check ciftleri (incidentResponder degismemis, schedule uzunlugu/hash degismemis, scheduleId commitment eslesmesi, FREEZE_WINDOW/MIN_NOTICE kisitlari, sonraki zamanlanmis upgrade'i gecmeme kontrolu) kapsamli; sadece bir ONCHAIN cagri (delayTimestamp) uretiyor, salt-okunur state'e dayanarak kendi kendini dogruluyor.
* UpdateVerifierHashes.s.sol + DeployAggregateVerifier.s.sol (standby): AggregateVerifier'in TUM parametrelerinin (anchorStateRegistry, DGF, DELAYED_WETH, TEE/ZK verifier adresleri, CONFIG_HASH, L2 parametreleri) eski/yeni arasinda AYNI kalmasini, sadece uc hash alaninin (TEE_IMAGE/ZK_RANGE/ZK_AGGREGATE) degismesini zorluyor; BASE_CONTRACTS_COMMIT sabit pin'e (8c21f6d...) kilitli - hem Solidity hem python check_verifier() ayni pin'i kontrol ediyor (cift katman).
* SetTEEProverRegistryImpl.s.sol (archive): EIP-1967 implementation slot sabiti (0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc) bagimsiz olarak keccak256('eip1967.proxy.implementation')-1 hesaplanarak DOGRULANDI - dogru. Registry state digest (owner/manager/gameType/proposer-challenger validity/signer listesi+imageHash+validSigner) upgrade/rollback her iki yonde de degismemesini zorluyor; NitroValidator/CertManager zincirinin (p384Verifier, owner, revoker, root sertifika) tam esleme kontrolu var.
* UpdateSigners.s.sol (active/common): Gnosis Safe owner ekleme/cikarma, OwnerDiff.json'dan okunan listeyi sanal bagli-liste ile simule ederek removeOwner icin DOGRU prevOwner'i hesapliyor (on-chain linked-list kaymasini dogru modelliyor); ekleme/cikarma oncesi zaten-owner/duplicate kontrolleri var.
* Genel desen: tum script'ler MultisigScript._buildCalls() + _preCheck/_postCheck ciftiyle calisiyor; nihai guvenlik siniri imzalayan guvenlik konseyi/signer'larin task-signing-tool (onceki turda incelendi) ile simulasyonu gorup onaylamasi. Bu depodaki potansiyel 'bug', sadece KOTU NIYETLI BIR PR script mantigini bozup gecerse (orn. bir kontrolu kaldirip) anlam kazanir - bu da GitHub PR inceleme surecine (Base ekibinin kod incelemesi) dayanir, kod enjeksiyonu/kimlik dogrulama atlama degil.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._