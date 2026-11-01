# Bug Bounty Raporu — Uniswap_v4-core

**Tarih:** 2026-11-01 07:25 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** confidence >= 90 ve verdict == PASS

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** Immunefi Official Public Bug Bounty Program (https://immunefi.com/bug-bounty/uniswap/) — Exact Matching Repository: https://github.com/Uniswap/v4-core (src/PoolManager.sol, src/libraries/Pool.sol, src/libraries/Hooks.sol)
* **Ham veri kaynağı:** `scripts/bugbounty/out/Uniswap_v4-core/raw`
* **Engellenen/erişilemeyen adımlar:** Program sayfasi bu ortamdan dogrulanamadi (ag politikasi); scope iddiasi gonderimdeki metne dayaniyor. Yalnizca halka acik kaynak kodun statik incelemesi., 10-06 ve 10-09 gonderimleri BIREBIR ayni (ayni SHA-256); tek hedef olarak islendi., Saglanmayan dosyalar: SwapMath.sol, SqrtPriceMath.sol, TickMath.sol, TickBitmap.sol, Position.sol, ProtocolFees.sol, ProtocolFeeLibrary.sol, ERC6909Claims.sol, CurrencyDelta/CurrencyReserves/NonzeroDeltaCount/Lock (transient storage kutuphaneleri), BalanceDelta/BeforeSwapDelta/Slot0 tipleri, SafeCast, LPFeeLibrary. Ozellikle (a) ERC6909Claims._burnFrom yetkilendirmesi, (b) SwapMath yuvarlamasi, (c) transient-storage delta muhasebesi DOGRULANAMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* DELTA MUHASEBESI: unlock() -> callback -> NonzeroDeltaCount != 0 ise CurrencyNotSettled revert; take/settle/clear/mint/burn hepsi onlyWhenUnlocked ve _accountDelta uzerinden. clear() yalnizca TAM pozitif delta'yi silebiliyor (amountDelta != current ise revert). mint/burn'de id currency.toId() ile kanonlastiriliyor (id'nin ust bitleriyle sahte-id yok).
* settle: reservesNow - reservesBefore (checked cikarma) ile odeme farki hesaplaniyor; fee-on-transfer token icin dogru (gercek gelen miktar kredilenir). sync() yetkisiz ama ayni islem icinde gecici (transient) durum; cross-tx etkisi yok.
* HOOKS: hook adres bitleri izin belirliyor, isValidHookAddress delta-donus bayraklarinin ilgili action bayragi olmadan acilmasini engelliyor. callHook: donus uzunlugu >= 32 ve selector eslesmesi zorunlu (EOA/bos donus InvalidHookResponse). beforeSwap: lpFeeOverride yalnizca dinamik ucretli havuzda okunuyor; hook delta'si exactIn<->exactOut tipini degistiremiyor (HookDeltaExceedsSwapAmount). afterSwap'ta (amountSpecified<0 == zeroForOne) yon secimi specified/unspecified eslemesi her dort kombinasyonda dogru.
* Pool.swap: protokol ucreti kesintisi unchecked blokta — delta = floor(toplam*protocolFee/1e6) <= feeAmount (feeAmount yukari yuvarlanan SwapMath ciktisi, swapFee >= protocolFee) oldugundan alttan tasma uretemez; swapFee==protocolFee dalinda delta=feeAmount. feeGrowthGlobal icin UnsafeMath.simpleMulDiv: feeAmount >= 2^128 olsa bile swapDelta'daki toInt128 donusumleri tum islemi revert ettiriyor (exactIn: amountSpecified-remaining, exactOut: amountCalculated).
* updateTick assembly paketleme: shl(128, liquidityNet) ust bitleri disari atiyor, liquidityGrossAfter maskeleniyor — kirli ust bit riski yok. tickSpacingToMaxLiquidityPerTick assembly'si yorumdaki referans formulle tutarli. crossTick/getFeeGrowthInside unchecked cikarma Uniswap'in bilincli modulo-aritmetik tasarimi.
* donate: toInt128 (checked) cagrilari simpleMulDiv'den ONCE; sifir likidite revert (NoLiquidityToReceiveFees). Havuz baslatma izinsiz ve beforeInitialize hook'u state'ten once cagriliyor ama cift-baslatma _pools[id].initialize'daki PoolAlreadyInitialized ile engelleniyor.
* SONUC: PoolManager.sol, Pool.sol ve Hooks.sol'de somut kanitli aciklik BULUNMADI. Yukaridaki eksik dosyalar (ozellikle ERC6909Claims yetkisi ve SwapMath) olmadan denetim TAM degil.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥90 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._