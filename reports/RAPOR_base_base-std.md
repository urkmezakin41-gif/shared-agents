# Bug Bounty Raporu — base_base-std

**Tarih:** 2026-11-03 09:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/base-std (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: Solidity. Description: A collection of Solidity interfaces, libraries, and mock implementations for Base precompiles..
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_base-std/raw`
* **Engellenen/erişilemeyen adımlar:** Bu depo, gercek precompile UYGULAMASINI (base/base'in Rust kod tabaninda) icermiyor -- sadece Solidity ARAYUZLERI, kutuphaneler ve mock implementasyonlar + fork/smoke test altyapisi barindiriyor. Gercek erisim-kontrolu/durum-degisikligi mantigi Rust tarafinda oldugu icin (ayri bir hedef, base_base, bu oturumda zaten incelendi), burada yalnizca arayuz tanimlarinin DOGRULUGU/TUTARLILIGI degerlendirilebildi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base'in 'B20' varlik standardi (ERC-20 benzeri ama politika/dondurma/el-koyma (seize) ve aktivasyon-kapisi destegi eklenmis) icin Solidity ARAYUZLERI + kapsamli bir fork/smoke test altyapisi (Python). Gercek precompile mantigi bu depoda degil, ayri base_base deposunun Rust kod tabaninda -- bu oturumda base_base zaten incelenmisti.
* Son iki commit: (1) `test/unit/PolicyRegistry/dispatch_inactive.t.sol`'daki `POLICY_DISPATCH_FIX` feature-flag gated test'inin KALDIRILMASI -- bu, 'bilinmeyen secici (selector), aktivasyon kapisindan ONCE siniflandirilmali, FeatureNotActivated ile MASKELENMEMELI' seklindeki onceden-bilinen bir dispatch-siralama hatasinin artik pinned Rust implementasyonuna gectigini ve test suite'in buna gore guncellendigini gosteriyor -- YENI bir acik degil, GECMISTE-ZATEN-DUZELTILMIS bir hatanin test-altyapisi takibi; (2) yalnizca .claude/skills/ altinda dokumantasyon/skill-sablonu degisiklikleri (adr-writer, changelog-gap-check, design-council) -- kod etkisi yok.
* `seizeWithMemo()` (IB20.sol) ve ilgili smoke test journey'si (`script/smoke/journeys/seize.py`) detaylica incelendi: fonksiyon imzasi, `Seized`/`Memo` olay imzalari ve hata adlari (InvalidSender, InvalidReceiver, AccountNotSeizable) arayuz ile test beklentileri arasinda TAM ESLESIYOR. Test, kendine-el-koyma (self-seize), sifir-adres kaynak/hedef, yetkisiz-hesap el-koyma ve el-koymanin transfer/executor politikalarini kasitli olarak atladigini (idari islem oldugu icin) dogru sekilde kapsiyor -- tasarimda bir eksiklik bulunamadi.
* F1 disinda, arayuz dosyalari (IB20.sol, IB20Asset.sol, IB20Factory.sol, IB20Stablecoin.sol, IBaseTime.sol, IERC165.sol, IERC8056.sol) ve Python test-altyapisi dosyalarinda (lint.py, mutate.py, smoke/*) tehlikeli kod-calistirma paternleri (eval/exec/shell=True/pickle.load) icin grep yapildi -- bulunamadi.
* SONUC: Bir dokumantasyon-tutarsizligi (F1, bulgu-degeri dusuk/bilgilendirici) disinda, HackerOne-raporlanabilir bir guvenlik acigi TESPIT EDILEMEDI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 10 | REJECT | Metin karsilastirmasiyla DOGRULANABILIR gercek bir tutarsizlik (deactivate()'in NatSpec'i var olmayan bir AlreadyDeactivated hatasina atifta bulunuyor) -- ancak bu saf bir ARAYUZ (interface) dosyasi, hic fonksiyon govdesi/mantigi icermiyor, bu nedenle istismar edilebilir bir KOD YOLU olusturmuyor. Gercek erisim-kontrolu ve revert davranisi, bu depoda OLMAYAN, ayri bir Rust precompile implementasyonunda yasiyor (zaten ayri bir hedef olarak -- base_base -- bu oturumda incelendi). HackerOne-raporlanabilir bir guvenlik acigi degil, salt bir dokumantasyon/spesifikasyon duzeltmesi onerisi. Confidence=10, hint-tier'e yonlendiriliyor. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._