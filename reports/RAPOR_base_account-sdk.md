# Bug Bounty Raporu — base_account-sdk

**Tarih:** 2026-11-03 07:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/account-sdk (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_account-sdk/raw`
* **Engellenen/erişilemeyen adımlar:** Signer.ts dosyasinin TAM hali teslim edilmedi (yalnizca diff parcasi) -- degisikligin cevresindeki kodun tam baglami (ornegin wallet_getSubAccount'un chainId'yi nasil kullandigi) tam olarak goruntulenemedi, ancak verilen diff + test dosyasi degisikligin dogrulugunu degerlendirmek icin yeterliydi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base'in istemci-tarafi cuzdan/odeme SDK'si (base/account-sdk, 'Pay with Base', alt-hesap/spend-permission destegi, popup-tabanli Signer). Yuksek deger tasiyan bir hedef (dogrudan fon hareketi ve imzalama akislari icerir), bu nedenle genis kapsamli incelendi.
* Son iki commit: (1) sadece versiyon/CHANGELOG guncellemesi (2.5.13 -> 2.6.0); (2) ONEMLI bir ozellik/duzeltme commit'i (#419, 'multi-chain deployed subaccount support') -- bu, `Signer.ts`'teki alt-hesap (sub-account) onbellekleme mantigindaki GERCEK bir hatayi DUZELTIYOR: eskiden `wallet_addSubAccount`/`wallet_getSubAccount` yalnizca adres eslesmesine bakarak onbellekteki alt-hesabi donduruyordu, chainId'yi HIC kontrol ETMIYORDU -- bu, ayni adrese sahip ama farkli zincirlerde farkli durumda olan (orn. bir zincirde deploy edilmis, digerinde edilmemis) alt-hesaplar arasinda karisikliga yol acabilirdi. Yeni kod `normalizeChainId()` ile istenen ve onbellekteki chainId'yi karsilastiriyor, uyusmazlikta onbellegi atlayip gercek popup istegini yapiyor; ayrica chainId belirtilmeden yeni bir alt-hesap eklendiginde eski chainId'yi temizliyor (stale veri birikmesini onluyor). Degisiklik TESTLERLE (3 yeni test case: chainId uyusmazliginda onbellek atlaniyor, eski chainId temizleniyor, hex/malformed chainId normalizasyonu) dogrulanmis -- bu bir GUVENLIK IYILESTIRMESI, yeni bir acik DEGIL.
* `Communicator.ts` (popup postMessage koprusu): `onMessage` dinleyicisinde `event.origin !== this.url.origin) return;` ile KATI origin dogrulamasi mevcut; `postMessage` cagrisi hedef origin'i `'*'` degil `this.url.origin` olarak belirliyor -- cross-origin mesaj enjeksiyonu riski yok (coinbase-wallet-sdk'nin ayni paterni ile tutarli, onceki oturumda da dogrulanmisti).
* Odeme/spend-permission dogrulama zinciri (validateUSDCBasePermission.ts, assertPermissionAuthorization.ts, validation.ts, translatePayment.ts): chainId+token-adresi ciftinin beklenen USDC/Base degerleriyle tam eslesmesi zorunlu tutuluyor; `assertPermissionAuthorization()` guvenilmeyen kaynaktan (tarayici) gelen subscription ID'lerini bilinen spender/payer adreslerine BAGLAMA icin acikca tasarlanmis (yorum: 'Use this when a subscription ID comes from an untrusted source'); tutar/adres girdi dogrulamasi (`validateStringAmount`, `normalizeAddress`, `validateDataSuffix`) viem'in denetlenmis `getAddress`/`isHex` fonksiyonlarini kullaniyor; ERC20 transfer encoding'i viem'in `parseUnits`/`encodeFunctionData` ile yapiliyor (ozel/riskli bir decimal-donusum mantigi yok).
* `createCdpClientOrThrow.ts`: CDP kimlik bilgileri ortam degiskenlerinden veya acik parametrelerden okunuyor, hata mesaji kimlik bilgilerinin KENDISINI sizdirmiyor (yalnizca nereden alinacagini anlatan genel bir yonlendirme metni).
* Genel tarama: dangerouslySetInnerHTML, eval, sabit kodlanmis gercek sir/anahtar, postMessage'da '*' hedef-origin kullanimi icin tum teslim edilen dosyalar grep edildi -- bulunamadi.
* SONUC: Teslim edilen veri (bir guvenlik-iyilestirici bug-fix commit'i + 70+ tam dosya statik incelemesi, odeme/imzalama/postMessage akislarina odaklanarak) icinde PASS veya hint-tier seviyesinde raporlanabilir bir YENI guvenlik acigi TESPIT EDILEMEDI. Temiz rapor (findings=[]) teslim ediliyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._