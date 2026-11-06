# Bug Bounty Raporu — base_task-signing-tool

**Tarih:** 2026-11-01 19:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/base/* (structured_scope id 1028889, max_severity critical, kullanici blogu). Blok varliga UYUYOR (base/task-signing-tool). 'Critical/High/Medium oduyor' iddiasi dogrulanamadi.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_task-signing-tool/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; calistirilmadi (eip712sign/Ledger/Trezor/forge/contract-deployments yok). Next.js dev sunucusuna karsi canli CSRF/DNS-rebinding denemesi yapilamadi., Eksik: contract-deployments repo (Makefile 'deps', task klasorleri), @sigstore/verify surum davranisi, next.config (bind adresi).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Incelenen ve temiz bulunan: path traversal (assertWithinDir + regex, config dosya adi icin ikinci assertWithinDir), execFile argv (shell yok), hash dogrulama (regex), Trezor yolunda typedData->hash eslesmesi, task-origin dogrulamasi (sigstore: zincir sabitleme, enjekte edilen CA'lar sabit ara CA'ya dogrulaniyor, SAN regex yerine tam eslesme kontrolu, tsaThreshold 1), simulasyon origin basarisizsa atlaniyor.
* Tasarim siniri (zafiyet degil): imzali tarball yalnizca config/<network> klasorunu kapsiyor; forge script kaynagi ve lib/ ayri. Ledger yolunda cihaz yalniz ham hash gosterir (blind) -> kullanici UI'daki hash'i karsilastirmali; Trezor yolunda typedData cihazda gosterilir.
* Son commit'ler: skipTaskOriginValidation 'match' sayilmaktan cikarildi ve ledgerId artik dogrulanmis config'ten geliyor; ikisi de guvenlik acisindan iyilestirme.
* Calisan bir exploit yok; yeni/az denetlenen ama saldiri yuzeyi dar bir yerel arac.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 25 | REJECT | Cevap CORS'suz opak; imza disari sizmaz; donanim cuzdani onayi gerekir; DNS rebinding/LNA kanitlanmadi. Bounty seviyesinde etki yok. |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._