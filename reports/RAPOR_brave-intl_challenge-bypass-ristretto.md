# Bug Bounty Raporu — brave-intl_challenge-bypass-ristretto

**Tarih:** 2026-11-01 21:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) - SOURCE_CODE wildcard https://github.com/brave/*, https://github.com/brave-intl/* (structured_scope id 943222, eligible_for_bounty: true, max_severity: critical). Blok varliga UYUYOR (challenge-bypass-ristretto-ffi / -wasm / upload-settlements). 'Critical' iddiasi blokta var; fork/arsiv durumu dogrulanamadi.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave-intl_challenge-bypass-ristretto/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; Rust/cgo ile derleme veya calistirma yapilmadi., Eksik: challenge-bypass-ristretto (Rust crate 2.1.0: voprf.rs/oprf.rs, rederive_unblinded_token_rfc, hash_to_group, DLEQ/batch verify), challenge-bypass-server (Go tuketici: Kafka/HTTP redeem akisi), Makefile/build.rs.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* FFI Rust katmani (src/lib.rs): null kontrolleri, Box::into_raw/from_raw sahiplik cifti, base64 decode UTF-8 kontrolu ve hata yutulmasi tutarli; yeni _rfc fonksiyonlari identity-element hatasini null+last_error ile donduruyor. Alt-seviye guvenligi bagimli crate'e (teslim edilmedi) dayaniyor.
* Kucuk notlar: batch_dleq_proof_new hata dalinda son 'null pointer' mesaji gercek hatayi eziyor (kozmetik). batch_dleq_proof_invalid_or_unblind null Token'lari filter_map ile sessizce eliyor; uzunluk uyusmazliginda copy_from_slice panic'i FFI sinirini asar (abort) — Go sarmalayicisi nil gecirmedigi surece erisilemez. err.source().unwrap() kutuphanenin TokenError->source garantisine dayaniyor.
* Son commit: CI make --old-file=src/lib.h (yalniz CI), crate 2.0.4->2.1.0, RFC 9497 varyantlari eklendi. Kripto dogruluk incelemesi (hash_to_group, DLEQ) icin crate kaynagi gerekli.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 4 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 30 | REJECT | Dil seviyesinde dogru ama tuketici erisilebilirligi kanitsiz; kutuphane sertlestirmesi. |
| F2 | 15 | REJECT | Teorik yaris, kanit ve saldirgan kontrolu yok. |
| F3 | 5 | REJECT | Istemci tarafi kendi kendine panic; guvenlik siniri yok. |
| F4 | 5 | REJECT | Operator araci, saldirgan girdisi yok. |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._