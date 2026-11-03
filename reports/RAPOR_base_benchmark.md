# Bug Bounty Raporu — base_benchmark

**Tarih:** 2026-11-03 06:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/benchmark (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: Go. Description: Benchmarking tool for OP stack chains.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_benchmark/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base'in OP-stack zincirleri icin performans-olcme (benchmark) araci (Go backend + React 'report' dashboard + Solidity is-yuku sozlesmeleri). Son iki commit SADECE report/src/metricDefinitions.ts icindeki statik dashboard metrik-etiket/aciklama metinlerine (yeni validity-predicate builder metrikleri icin) ekleme yapmis -- calisan mantik degil, salt goruntuleme konfigurasyonu.
* F1 disinda, Go backend (runner/benchmark/*, runner/clients/*), React dashboard (report/src/*) ve is-yuku Solidity sozlesmeleri (ERC20Transfer.sol, Precompile.sol, Simulator.sol -- bunlar kasitli olarak agir/stres-testi sozlesmeleri, guvenlik acigi degil tasarim) tam incelendi; dangerouslySetInnerHTML, eval, sabit kodlanmis gercek sir, SQL/komut enjeksiyonu paternleri icin grep yapildi -- F1 disinda baska bir sorun bulunamadi.
* F1, kod-okumasi ile kesin olarak dogrulanabilen gercek bir girdi-dogrulama hatasi (Go slice panic'i) -- ancak etki alani dar: yalnizca dahili benchmark RPC proxy'sinin tek bir istek/baglantisini kesintiye ugratiyor (Go'nun otomatik panic-recovery'si tum sureci korur), uretim zincir/fon/konsensus etkisi yok. Bu nedenle Stage 2'de dusuk guven/REJECT ile hint-tier'e yonlendirilmesi onerilir (benzer sekilde bu oturumda daha once 'self-harm-only etki' sinifindaki bulgular icin uygulanan tutarli kalibrasyon).
* SONUC: Bir gercek ama dusuk-etkili kod kalitesi/girdi-dogrulama bulgusu (F1) tespit edildi; baska bir guvenlik acigi bulunamadi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 25 | REJECT | Bulgu kod-okumasi ile DOGRULANABILIR gercek bir hata (Go'da `rawTxHex[2:]` dilimlemesi, `len(rawTxHex) < 2` oldugunda panic firlatir, kontrol yok) -- ancak bu bir HackerOne-raporlanabilir guvenlik acigi barajini GECMIYOR: (1) Etkilenen bilesen Base'in uretim zincir altyapisi degil, dahili/yerel bir performans-olcme (benchmark) aracinin RPC proxy'si -- kullanici fonu, veri gizliligi veya konsensus guvenligi etkilenmiyor. (2) Go'nun net/http sunucusu panikleri OTOMATIK OLARAK yakalar (recover()) ve sadece o baglantiyi kapatir -- tum proxy sureci veya host'taki diger hizmetler etkilenmiyor, bu da 'DoS' etiketini zayiflatiyor (gercek etki: tek bir istegin basarisiz olmasi + log satiri). (3) Somut, ag-uzerinden sunulmus bir istismar KANITI (gercek bir calistirma, paket yakalamasi) sunulmadi -- yalnizca statik kod okumasina dayanan bir cikarim. (4) Benchmark araclari tipik olarak izole/gecici CI ortamlarinda veya yerel makinede calistirilir; `:port` dinleme adresinin fiilen genel internete acik oldugunu gosteren bir dagitim/altyapi kaniti yok. Confidence=25, hint-tier'e yonlendiriliyor: bir sonraki benchmark PR'inda `strings.HasPrefix`/uzunluk kontrolu eklenmesi onerilir, ancak tam RAPOR_<hedef>.md + Telegram bildirimi seviyesinde bir guvenlik acigi degil. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._