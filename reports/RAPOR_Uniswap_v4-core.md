# Bug Bounty Raporu — Uniswap_v4-core

**Tarih:** 2026-11-01 07:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** confidence >= 90 ve verdict == PASS

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** Immunefi Official Public Bug Bounty Program (https://immunefi.com/bug-bounty/uniswap/) — Exact Matching Repository: https://github.com/Uniswap/v4-core (src/PoolManager.sol, src/libraries/Pool.sol, src/libraries/Hooks.sol)
* **Ham veri kaynağı:** `scripts/bugbounty/out/Uniswap_v4-core/raw`
* **Engellenen/erişilemeyen adımlar:** Program sayfasi bu ortamdan dogrulanamadi (ag politikasi); scope iddiasi gonderimdeki metne dayaniyor. Yalnizca halka acik kaynak kodun statik incelemesi., Ayni hedef uc kez gonderildi (10-06, 10-09 birebir ayni; 10-33 ise 8 ek dosya iceriyor). Bu tur 10-33 surumunun tamami okundu., Hala saglanmayan dosyalar: FullMath, UnsafeMath, TickMath, TickBitmap, Position, ProtocolFeeLibrary, LPFeeLibrary, CurrencyReserves, SafeCast, Currency/BalanceDelta/BeforeSwapDelta/Slot0 tipleri, CustomRevert. Ozellikle FullMath.mulDiv/mulDivRoundingUp ve TickMath/TickBitmap dogrulugu bu turda VARSAYILDI, incelenmedi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* ONCEKI TURDAN KAPANAN ACIK SORULAR: (a) ERC6909Claims._burnFrom yetkisi DOGRU: from != msg.sender ve operator degilse allowance[from][sender][id] kontrol ediliyor ve dusuruluyor (max ise dusurulmuyor, ERC6909 standardi); PoolManager.burn(from, ...) baskasinin claim token'ini yetkisiz yakamaz. (b) SwapMath/SqrtPriceMath incelendi (asagida). (c) Transient storage delta muhasebesi: CurrencyDelta.applyDelta int256 + int128 (checked), _accountDelta'daki next==0/previous==0 mantigi NonzeroDeltaCount'u tutarli tutuyor; decrement'in assembly'de alttan tasmasi yalnizca previous != 0 (yani sayaca katkisi olan) durumda cagriliyor.
* SwapMath.getSqrtPriceTarget assembly'si zeroForOne icin max(next, limit), degilse min(next, limit) donduruyor (iki dalda da dogrulandi). computeSwapStep: exactIn'de amountIn yukari, amountOut asagi yuvarlaniyor; hedefe ulasilirsa feeAmount=mulDivRoundingUp(amountIn, fee, 1e6-fee), ulasilmazsa kalan tum girdi ucret sayiliyor (feeAmount = -amountRemaining - amountIn, alttan tasma yok cunku amountIn <= amountRemainingLessFee). Ucret %100'de exactIn: amountIn=0, fiyat degismiyor, tum girdi ucret — dongu sonlaniyor. Sifir likidite: getAmountDelta=0 oldugundan hedef dala giriyor, getNextSqrtPriceFrom* (likidite 0'da revert eden) cagrilmiyor.
* SqrtPriceMath: getNextSqrtPriceFromAmount0RoundingUp/Amount1RoundingDown v3'teki yuvarlama yonleriyle birebir (girdide fiyati hedefi gecmeyecek, ciktida gececek sekilde); tasma/yetersiz-likidite kontrolleri (PriceOverflow, NotEnoughLiquidity) assembly'de dogru. getAmount1Delta icindeki absDiff assembly'si iki isaret icin de |a-b| donduruyor. Isaretli getAmount0/1Delta: ekleme (liquidity>=0) negatif+yukari yuvarlama (kullanici oder), cikarma pozitif+asagi yuvarlama.
* ProtocolFees: setProtocolFee / collectProtocolFees yalnizca protocolFeeController; setProtocolFeeController onlyOwner. collectProtocolFees sync edilmis para birimini toplamayi engelliyor (sync-settle arasinda bakiye degisimi). protocolFeesAccrued -= (checked).
* HOOKS / POOLMANAGER (onceki turdan): delta muhasebesi, hook delta isaret mantigi (4 kombinasyon), lpFeeOverride yalnizca dinamik havuzda, Pool.swap unchecked protokol ucreti blogu, assembly paketleme — hepsi tutarli.
* SONUC: PoolManager, Pool, Hooks ve 8 yeni dosyada (ERC6909Claims, ERC6909, ProtocolFees, SwapMath, SqrtPriceMath, CurrencyDelta, NonzeroDeltaCount, Lock) somut kanitli aciklik BULUNMADI. FullMath/TickMath/TickBitmap/Position gibi kalan dosyalar incelenmedi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥90 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._