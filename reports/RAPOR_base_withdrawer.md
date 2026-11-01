# Bug Bounty Raporu — base_withdrawer

**Tarih:** 2026-11-01 16:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/base/* (structured_scope id 1028889, eligible_for_bounty: true, max_severity: critical) -> hedef https://github.com/base/withdrawer. Blok varlikla eslesiyor; program sayfasi bu ortamdan dogrulanamadi.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_withdrawer/raw`
* **Engellenen/erişilemeyen adımlar:** Program sayfasi bu ortamdan dogrulanamadi; statik inceleme, kod calistirilmadi., Okunan: main.go (iki dosya), withdraw/fpwithdraw.go, signer/*, withdraw/withdraw.go ve utils.go yuzeysel; bindings/anchor_state_registry.go uretilmis kod (taranmadi); *_test.go dosyalari okunmadi. Bagimliliklar (ethereum-optimism op-node withdrawals/bindings) paket disi: ProveWithdrawalParametersFaultProofs, FindLatestGame gibi yardimcilarin dogrulugu hakkinda hukum verilmedi.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] main.go --private-key ve --mnemonic bayraklari gizli anahtari komut satirinda aliyor (islem argumanlarinda/kabuk gecmisinde gorunebilir). Yerel CLI araci icin bilinen/yaygin bir tasarim; uzaktan istismar yolu yok -> odul disi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* FPWithdrawer akisi (CheckIfProvable, ProveWithdrawal, FinalizeWithdrawal, GetProvenWithdrawalTime): cekirdek mantik OP kutuphanelerinin (withdrawals.ProveWithdrawalParametersFaultProofs, ParseMessagePassed, WithdrawalHash) uzerine ince bir sarmalayici. Portal.CheckWithdrawal ile kesinlestirmeden once on kontrol yapiliyor; dispute game kara listede/emekli ise ispat gecersiz sayiliyor (isDisputeGameInvalidated). NoSend/DryRun yollari islem gondermeden gaz simulasyonu yapiyor. Tutar/hedef alanlari dogrudan L2 makbuzundaki MessagePassed olayindan geliyor (kullanici girdisi degil).
* Imzalayici: ecdsaSigner yerel anahtarla crypto.Sign, walletSigner ledger/trezor icin accounts.Wallet.SignTx; mnemonic turetimi bip39 + hdkeychain; hata kontrolleri var. Yeniden deneme katmani (retryingL2/NewRetryingBackend) yalnizca RPC hatalarini yeniden deniyor; imzali islem yeniden gonderiminde sendTransaction ile ayni imzali tx kullaniliyor (ciftli gonderim sorunu gosterilemedi).
* SONUC: Okunan dosyalarda kod kanitli bir zafiyet BULUNAMADI. Bu bir kullanici-tarafi CLI; saldirgan modeli sinirli (kotu niyetli RPC saglayici en fazla yanlis veri dondurur ve islem on-zincir kontrollerinden gecer). 'Bulgu yok' yalnizca okunan dosyalar icin gecerlidir.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._