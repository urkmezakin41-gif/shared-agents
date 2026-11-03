# Bug Bounty Raporu — base_base

**Tarih:** 2026-11-03 05:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/base (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: Rust. Description: All components used to run Base.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_base/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base'in ana node/konsensus yazilimi (base/base, Rust). Son iki commit'ten biri sadece README metin duzenlemesi (a602534f99); ikincisi (cd37e0cfb0) ONEMLI bir EIP-8130 (Base'e ozel yeni islem/gaz-olcumleme protokolu) yeniden-adlandirma/refaktor commit'i -- bu, protokol-kritik gaz muhasebesi (intrinsic gas, payer authentication, fee settlement) kodunu etkiledigi icin satir-satir dikkatle incelendi.
* EIP-8130 refaktor diff'i (crates/common/consensus/.../eip8130/signed.rs, crates/common/eip8130/intrinsic.rs, crates/common/evm/eip8130.rs, crates/common/precompiles/tx_context/storage.rs, crates/execution/eip8130{,-rpc}/*, crates/execution/txpool/validator.rs): `payer_auth`->`payer_floor`, `payer_auth_standard`->`payer_auth_cost` alan adlari TUM cagiran noktalarda (txpool validator, EVM executor, intrinsic gas hesabi, testler) TUTARLI sekilde degistirilmis -- deger hesaplamalari matematik olarak AYNI (eski `sender_intrinsic() = total() - payer_auth` yerine artik dogrudan ayni bilesenlerin toplanmasi; `total()` metodu kaldirilmis ama hicbir yerde artik kullanilmiyor). Fonksiyonel bir fark BULUNAMADI.
* `TxContextStorage::sender_actor_id()`: ozel `address_to_actor_id()` yardimci fonksiyonu kaldirilip yerine `self.storage.origin().into_word()` kullanilmis -- alloy_primitives::Address::into_word() standart donusumu (adres dusuk-sirali 20 bayt, yuksek 12 bayt sifir, yani eski elle-yazilan koddakiyle AYNI bayt duzeni) uyguluyor; davranis degismiyor, sadece olculu bir sadelestirme.
* `NonceValidator::replay_hash()` sarmalayici fonksiyonu kaldirilip cagiranlar direkt `tx.replay_id(account)` kullaniyor -- ayni alt-seviye fonksiyonu cagiriyor, davranis degismiyor.
* `settle_fees()`: `beneficiary` ve `spec` degiskenlerinin hesaplanmasi fonksiyon basindan fonksiyon icine (kullanildiklari yere) tasinmis (ctx.block().beneficiary() / ctx.cfg().spec()). Blok-seviyesi degerler (beneficiary, spec) bir islem yurutmesi sirasinda degismez, bu nedenle tasima guvenlidir.
* Acceptance/actions test harness dosyalari (acceptance/src/*, actions/harness/src/*) -- bunlar CI/entegrasyon test altyapisi, uretim zincir kodu degil. Yine de guvenlik pratikleri icin kontrol edildi: `Report::copy_report_evidence()` kanitlanmis dogru path-traversal/symlink koruma uyguluyor (canonicalize + starts_with + symlink_metadata kontrolu), ve eslesen test (`evidence/external-link.txt`, `evidence/parent-link`) bu korumanin calistigini aciyor dogruluyor. `Command::new("git").args([...])` kullanimi array-bazli argumanlar ile (shell interpolasyonu yok) -- komut enjeksiyonu riski yok. `CliRun::shell_quote()` yalnizca kullaniciya gosterilecek 'inert reproduction text' (kopyala-yapistir komutu) icin dogru shell-escaping yapiyor, programin kendisi tarafindan calistirilmiyor.
* Test harness icindeki sabit kodlanmis anahtarlar (`PrivateKeySigner::from_bytes(&B256::repeat_byte(0xBA))`, `TEST_ACCOUNT_KEY`) acikca tekrarlanan-bayt-paternli test/dummy anahtarlar -- gercek sir degil, standart test fixture paterni.
* Genel tarama: `unsafe{}` blok kullanimlari, hardcoded gercek-gorunumlu ozel anahtarlar/sirlar, shell enjeksiyonu paternleri icin tum teslim edilen dosyalar grep edildi -- riskli bir kullanim bulunamadi.
* SONUC: Teslim edilen veri (bir onemli protokol-refaktor commit'i, tam satir-satir dogrulandi + 24 tam dosya statik incelemesi) icinde PASS veya hint-tier seviyesinde raporlanabilir bir guvenlik acigi TESPIT EDILEMEDI. EIP-8130 yeniden-adlandirma commit'i matematik olarak esdeger; test harness guvenlik pratikleri (symlink koruma, array-bazli komut calistirma) dogru uygulanmis. Temiz rapor (findings=[]) teslim ediliyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._