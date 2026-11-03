# Bug Bounty Raporu — base_account-policies

**Tarih:** 2026-11-03 13:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/account-policies (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: Solidity. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_account-policies/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base Smart Wallet icin 'account policy' (harcama/DeFi-etkilesim yetkilendirme) sozlesmeleri -- PolicyManager (merkezi koordinator), SingleExecutorPolicy/SingleExecutorAuthorizedPolicy (executor-imzali yetkilendirme), TransferSettingsPolicy (eski adiyla MoiraiDelegate, bu commit'te yeniden adlandirildi -- salt refactor), ve Morpho Blue entegrasyon politikalari (MorphoLendPolicy, MorphoLoanProtectionPolicy, MorphoWethLoanProtectionPolicy). YUKSEK DEGERLI bir hedef (dogrudan DeFi pozisyon/fon yonetimi).
* Son iki commit: (1) YENI `MorphoLtvLib.sol` kutuphanesinin eklenmesi + testleri (F1'in temelini olusturan commit); (2) `MoiraiDelegate` -> `TransferSettingsPolicy` yeniden adlandirmasi + testleri -- salt isim degisikligi, mantik degisikligi goze carpmiyor (diff'te fonksiyon govdelerinde anlamli bir fark yok, sadece sozlesme/dosya/test adlari).
* PolicyManager.sol'un trust-boundary dokumantasyonu (ReplacePayload struct'inin `oldPolicyReplaceData`/`newPolicyReplaceData` alanlarinin KASITLI olarak EIP-712 imzasi tarafindan kapsanmadigi, ve bu riskin policy implementasyonlarina acikca devredildigi) dikkatle incelendi -- bu, iyi belgelenmis, bilincli bir tasarim karari, yeni bir güvenlik acigi degil.
* MorphoLendPolicy.sol (basit, RecurringAllowance-sinirli Morpho vault depozito politikasi) LTV/liquidation hesaplamasi icermiyor -- F1'den etkilenmiyor.
* SECURITY.md (bu depoda mevcut degil ama base/bridge'de gorulen ayni politika gecerli -- base/* altindaki tum depolar icin): deployed smart contract'lar Cantina bug-bounty kapsaminda, HackerOne offchain bilesenler icin. F1 bir deployed smart contract'taki bulgu oldugundan, operator raporu Cantina'ya submit etmeyi dikkate almali.
* SONUC: Bir gercek, orta siddette, kod-okumasi ile kesin dogrulanan hassasiyet/yuvarlama-yonu bulgusu (F1) tespit edildi -- codebase'in KENDI yeni eklenen kutuphanesi, bu TAM sorunu cozmek icin tasarlanmis ama henuz entegre edilmemis.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 20 | REJECT | F1'i curutmeye calisirken ONEMLI bir nicel gercek ortaya cikti: `Math.mulDiv`'in Floor (varsayilan) ve Ceil modlari arasindaki fark, matematiksel olarak HER ZAMAN EN FAZLA 1 WAD-birimi (1e-18, yani %0.0000000000000001) -- girdi buyuklugunden BAGIMSIZ olarak. Bu, 'postTopUpLtv >= lltv' kontrolunun ANCAK pozisyonun TAM-hassasiyetli gercek LTV'si `lltv`'ye TAM OLARAK 1e-18 WAD icinde (knife-edge) olmasi durumunda 'yanlis' sonuc verebilecegi anlamina geliyor -- pratikte GERCEKLESMESI nerdeyse imkansiz derecede dar bir pencere (oracle fiyati, debt/collateral share oranlari ve topUpAssets'in TAM OLARAK bu mikroskopik araliga denk gelmesini gerektirir).

Daha da onemlisi, buradaki 'saldirgan-kurban' iliskisi net degil: bu, HESABIN KENDI yukledigi bir koruma politikasi -- 'saldirgan' senaryosu, hesabin kendi executor'unun kendi pozisyonunu 1e-18 WAD kadar daha az guvenli bir noktada 'basarili' olarak isaretlemesi anlamina gelir; bu durumda ZARAR GOREN taraf (varsa) HESABIN KENDISI olur, ucuncu bir taraf degil -- ve zarar bile anlamsizca kucuktur (Morpho'nun KENDI likidasyon mantigi, pozisyon gercekten lltv USTUNDEYSE zaten bagimsiz olarak likide edebilir; bu policy sadece bir 'best-effort' koruma katmanidir ve sozlesmenin kendi NatSpec'i de ACIKCA 'NOT guaranteed to prevent liquidation' diyor).

Bu nedenle F1, GERCEK ve DOGRULANABILIR bir kod-tutarlilik/hassasiyet sorunu olarak kaliyor (codebase'in KENDI yeni MorphoLtvLib kutuphanesi bunun TAM olarak cozulmesi gereken bir sorun oldugunu ima ediyor), ancak PRATIK istismar edilebilirligi sifira yakin (astronomik derecede dar bir pencere + belirsiz/onemsiz zarar + ucuncu-taraf saldirgan yok). Confidence=20, hint-tier'e yonlendiriliyor -- tam PASS/rapor seviyesinde bir guvenlik acigi degil, ancak 'defense-in-depth icin kod-tutarliligi' duzeltmesi olarak degerli bir not. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._