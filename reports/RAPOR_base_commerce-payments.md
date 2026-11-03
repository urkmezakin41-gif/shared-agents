# Bug Bounty Raporu — base_commerce-payments

**Tarih:** 2026-11-03 16:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/commerce-payments (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: Solidity. Description: Onchain authorization and capture for trust-minimized commerce..
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_commerce-payments/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base'in 'Commerce Payments Protocol' (yetkilendirme+yakalama escrow-tabanli odeme sistemi, Stripe-benzeri 'authorize then capture' modelini zincir-ustunde uygulayan) -- YUKSEK DEGERLI ama ONEMLI bir baglam: bu, ZATEN v1.1.0'a kadar UC AYRI PROFESYONEL DENETIMDEN (2x Spearbit/Cantina + Coinbase Protocol Security) GECMIS, mainnet'te YASAYAN, canli bir sozlesme ailesi. En SON denetim (07/22/2026, PR #90) ACIKCA 'rounding and billing change' konusunu kapsiyor -- yani TAM OLARAK supheleneceğim alan (ucret/rounding mantigi) zaten profesyonelce incelenmis ve duzeltilmis.
* Son iki commit TAMAMEN dokumantasyon (README deploy-adres tablosu guncellemesi v1.1.0 icin + Security.md'ye 3. denetim raporu eklenmesi) -- kod degisikligi YOK.
* AuthCaptureEscrow.sol (cekirdek escrow mantigi) tam incelendi: `charge`/`authorize`/`capture`/`void`/`reclaim`/`refund` fonksiyonlarinin TUMU dogru erisim kontrolune (`onlySender(paymentInfo.operator)` veya `onlySender(paymentInfo.payer)`), dogru zaman-penceresi kontrollerine (preApproval/authorization/refund expiry sirasi), ve dogru durum-gecisi muhasebesine (`capturableAmount`/`refundableAmount` arasinda SIKI sekilde korunan toplam) sahip. `_validateFee()`'nin minFee/maxFee hesabi (`amount * bps / 10_000`, varsayilan floor-rounding) HER IKI yonde de payer'i KORUYUCU yonde yuvarliyor (hem minFee hem maxFee asagi yuvarlaniyor -- operator'un asla izin verilenden fazla ucret alamayacagini garanti ediyor) -- bu TUTARLI, guvenli bir tasarim, yeni denetimin konusu olan degisiklikle TUTARLI gorunuyor.
* `_collectTokens()` escrow'a aktarilan token miktarini ONCESI/SONRASI bakiye farki ile DOGRULUYOR (`tokenStoreBalanceAfter != tokenStoreBalanceBefore + amount` -> revert) -- bu, fee-on-transfer token'lari veya hatali collector davranisini yakalayan guclu bir savunma katmani.
* TUM 5 collector (ERC3009PaymentCollector, Permit2PaymentCollector, PreApprovalPaymentCollector, SpendPermissionPaymentCollector, OperatorRefundCollector) + ERC6492SignatureHandler + TokenCollector(abstract) + TokenStore.sol tam incelendi: hepsi `collectTokens()`'i `onlyAuthCaptureEscrow` ile kisitliyor, imza/izin-tabanli mekanizmalarin (ERC-3009 nonce, Permit2 nonce, SpendPermission salt) TUMU `_getHashPayerAgnostic(paymentInfo)`'dan turetilen BENZERSIZ bir deger kullaniyor (payment-bazinda replay koruması), ve preApprovalExpiry ile deadline/end alanlarinin TUTARLI sekilde baglandigi dogrulandi. `PreApprovalPaymentCollector.preApprove()` dogru sekilde `msg.sender == paymentInfo.payer` zorunlu kiliyor.
* SONUC: Uc kez profesyonelce denetlenmis, mainnet'te canli calisan bu escrow odeme protokolunde (ozellikle en son denetimin KAPSADIGI rounding/billing alaninda dahil) PASS veya hint-tier seviyesinde raporlanabilir YENI bir guvenlik acigi TESPIT EDILEMEDI. Temiz rapor (findings=[]) teslim ediliyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._