# Bug Bounty Raporu — base_eip712sign

**Tarih:** 2026-11-03 11:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/eip712sign (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: Go. Description: Golang utility for signing EIP-712 payloads.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_eip712sign/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base'in EIP-712/EIP-191 imzalama CLI araci (`eip712sign`) -- ledger/trezor/mnemonic/raw-private-key ile imzalama destekliyor, tipik olarak `forge script` ciktisindan (governance/multisig/hazine islemleri) imzalanacak veriyi 'vvvvvvvv'...'^^^^^^^^' magic-string isaretleyicileri arasindan cekiyor. Bu, YUKSEK DEGERLI bir hedef (dogrudan imzalama/anahtar yonetimi) oldugu icin TUM kaynak kodu (main.go, tek dosya, ~600 satir) tam olarak okundu.
* Son iki commit SADECE go.mod/go.sum bagimlilik surum guncellemeleri (github.com/base/usbwallet v0.1.0->v0.1.1->v0.1.2, bir dolayli bagimliligin [karalabe/usb] kaldirilmasi) -- kod mantigi degisikligi yok.
* Kriptografik imzalama zinciri tamamen go-ethereum'un denetlenmis kutuphanelerine devrediliyor: `crypto.Sign()` (ECDSA), `apitypes.TypedDataAndHash()` (EIP-712), `accounts.TextHash()` (EIP-191), `usbwallet.Wallet.SignText/SignTypedData` (donanim cuzdanlari) -- OZEL/yeniden-uygulanmis bir kriptografi YOK. Recovery ID duzeltmesi (`sig[crypto.RecoveryIDOffset] += 27`) yalnizca yazilim-anahtari (ecdsaSigner) yolunda uygulaniyor, standart Ethereum v=27/28 konvansiyonuyla tutarli; donanim cuzdan yollari kendi cikis formatlarini zaten dogru uretiyor (usbwallet onceki oturumda ayrica incelenmisti).
* `derivePrivateKey()`: decred/dcrd/hdkeychain kutuphanesini SIFIR degerli (`fakeNetworkParams{}`) versiyon baytlariyla kullaniyor -- bu baytlar yalnizca serialize edilmis genisletilmis anahtar formatinin AG-TANIMA onekini etkiler, asil BIP32 anahtar turetme matematigini DEGISTIRMEZ; Ethereum topluluk araclarinda (Bitcoin-spesifik olmayan EVM zincirleri icin) yaygin, kabul edilmis bir teknik.
* Girdi ayristirma (prefix/suffix magic-string cikarma, hex/JSON otomatik tespiti, 66-bayt uzunluk kontrolu EIP-712 '0x1901 || domainSeparator || hashStruct' on-imaj yapisi icin) incelendi -- bu alanlarin ICERIK dogrulugunu (orn. `0x1901` sabitinin varligini) KONTROL ETMEDIGI goruldu, ancak bu BILINCLI bir tasarim secimi: arac, README'de belgelendigi gibi 'iki magic string arasindaki herhangi bir hex string'i imzalayan KASITLI OLARAK genel/minimal bir sarmalayici -- EIP-712 yapisal dogrulugunu garanti etmek operatorun KENDI `forge script`'inin sorumlulugunda (zaten guvenilir, operator tarafindan yazilan kod).
* F1 disinda, `exec.Command(name, args...)` array-bazli argumanlar kullaniyor (shell yorumlamasi yok, komut enjeksiyonu riski yok); `--private-key` bayraginin ham anahtari CLI argumani olarak almasi (shell history/process-list sizintisi) BILINEN, dokumante edilmis bir risk sinifi (aracin kasitli olarak sundugu bir ozellik, yeni bir kusur degil).
* SONUC: Dusuk etkili, operator-tetikli bir panic/crash bulgusu (F1) disinda, HackerOne-raporlanabilir bir guvenlik acigi TESPIT EDILEMEDI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 8 | REJECT | Kod-okumasiyla DOGRULANABILIR gercek bir hata (args[1] bounds-check yok) -- ancak HackerOne-raporlanabilir bir guvenlik acigi barajini GECMIYOR: (1) Tetikleyici girdi, bu araci calistiran OPERATORUN KENDI yazdigi CLI argumanlari (`-- forge` gibi) -- subprocess ciktisindan, bir agdan veya baska bir taraftan gelmiyor; disaridan/uzaktan hic bir sekilde erisilemez. (2) Etkisi: aracin, imzalama islemi BASLAMADAN ONCE bir panic ile cakismasi -- hicbir anahtar/imza sizintisi, yetkisiz imzalama veya baska bir tarafi etkileyen bir sonuc yok; tamamen zararsiz bir 'kendi komutunu yanlis yazarsan arac cakisir' senaryosu. (3) base_base-std oturumunda confidence 10 olan benzer-siniftaki bir bulgu hint-tier esigini (15) gecmemisti; bu bulgu DAHA DA az etkili (ag-erisimi bile yok), bu nedenle confidence=8 ile ayni sekilde esigin altinda tutuluyor. Tam rapor veya ipucu bildirimi uretilmiyor. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._