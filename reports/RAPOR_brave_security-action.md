# Bug Bounty Raporu — brave_security-action

**Tarih:** 2026-11-04 17:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/security-action (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: Composite GitHub CI Action containing the minimal viable security lint for brave repositories.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_security-action/raw`
* **Engellenen/erişilemeyen adımlar:** Teslim (386KB, ~11250 satir) BUYUK ama asil `action.yml` (composite action tanimi -- hangi adimlarin hangi SIRAYLA, hangi GITHUB-event TETIKLEYICISIYLE (orn. `pull_request` vs `pull_request_target` -- bu AYRIM, FORK'tan gelen bir PR'in SECRETS'e erisip-erismeyecegini belirleyen KRITIK bir GitHub Actions guvenlik SINIRIDIR) calistigini gosteren dosya) ve `assets/reviewdog/post-findings.sh`, `scripts/with-sandbox.sh` gibi BAZI SHELL betikleri bu teslimde YOK (sadece JS/Python kaynaklari ve test adimlari teslim edildi) -- bu nedenle 'bu action HANGI GUVEN SINIRINDA calisiyor' sorusu TAM olarak dogrulanamadi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in COK SAYIDA deposunda CI pipeline'inda calisan bir COMPOSITE GitHub Action -- potansiyel SUPPLY-CHAIN etkisi (bir acik, TUM depolari ETKILEYEBILIR) nedeniyle ozel dikkatle incelendi.
* `src/installLandrun.js` (ikinci-el ARAC/binary INDIRME + KURULUM -- klasik SUPPLY-CHAIN riski OLAN bir desen) OZELLIKLE DIKKATLE incelendi -- OLAGANUSTU IYI tasarlanmis: SABIT (pinned) SHA256 digest'leri, HER kurulumda VE her YENIDEN-KULLANIMDA digest DOGRULAMASI (fail-closed), 'remote install script' KULLANILMAMASI (dogrudan release-asset indirme), platform/mimari icin PINNED digest YOKSA aga HIC DOKUNMADAN HATA VERME. Digest DEGERLERININ UZUNLUGU (64 hex karakter = GECERLI SHA256) dogrulandi. HICBIR zafiyet bulunamadi.
* Genis-capli grep taramasi (TUM teslim, 11251 satir): `eval(`, `new Function(`, shell=True-benzeri PATTERN'LER -- HICBIRI bulunamadi. `execSync`/`spawnSync` cagrilarinin TUMU, PR-icerigi/dal-adi/commit-mesaji gibi SALDIRGAN-KONTROLLU VERIYI DOGRUDAN bir shell komutuna GOMMEDEN, kurulum-ic path'leriyle (bin, instDir) SINIRLI kullaniliyor -- klasik 'PR title/branch name command injection' deseni (GitHub Actions'ta YAYGIN bir zafiyet sinifi) icin bir ORNEK bulunamadi.
* F1 (CODEOWNERS desen-eslesme sapmasi) tespit edildi ama DUSUK-ETKI olarak degerlendirildi -- bu modulun TEK bulunan tuketicisi bir BILGILENDIRME yorumu POSTLUYOR, erisim-kontrolu DEGIL; GERCEK CODEOWNERS zorunlulugu GitHub'in KENDI native mekanizmasindan GELIYOR, bu JS araciNDAN DEGIL. Brave'in KENDI sembolik-dogrulama (ExpoSE) test suiti bu FONKSIYONU KAPSIYOR ama DAHA DAR bir invariant icin (segment-sinir), bu OZEL sapmayi YAKALAMAYACAK sekilde.
* `assets/opengrep_rules/` dizini (opengrep/semgrep KURALLARI -- bu araclarin KENDI TARADIGI guvenlik-desenleri) goz-gezdirildi, ancak bu dosyalar STATIK-ANALIZ KURAL TANIMLARI (yurutulebilir mantik DEGIL), inceleme-kapsami DISINDA tutuldu.
* SONUC: Bu COMPOSITE action'da, SUPPLY-CHAIN/kod-enjeksiyonu acisindan HICBIR somut GUVENLIK ACIGI bulunamadi (installLandrun.js OZELLIKLE ORNEK-TEŞKİL EDEN bir guvenlik-TASARIMI); SADECE DUSUK-ETKI bir CODEOWNERS desen-eslesme DOGRULUK sapmasi (F1, hint-tier'a deger) tespit edildi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 18 | REJECT | Kod-seviyesi IDDIAYI (ic-ice egik-cizgili desenlerin KOSULSUZ agac-genis eslestirilmesi) DOGRU buldum -- `patternToRegex`'in else kolunu TEKRAR OKUDUM, `(^|/)` oneki GERCEKTEN her BASTA-egik-cizgisi-OLMAYAN desene (ic-ice slash ICERSE DE) UYGULANIYOR, CURUTEMEDIM. ANCAK REJECT'E ITEN ana sebep: (1) Stage1'in KENDISI de DOGRU sekilde ITIRAF EDIYOR ki BU modulun bu teslimde BULUNAN TEK tuketicisi (`codeowners_comment.steps.js`) bir INFORMATIONAL PR-yorumu POSTLUYOR -- bir ERISIM-KONTROLU/approval-gate DEGIL; GERCEK CODEOWNERS zorunlulugu (orn. 'bu dosyayi degistiren bir PR, belirli bir takimin ONAYI OLMADAN merge EDILEMEZ') GitHub'IN KENDI native branch-protection+CODEOWNERS motorundan GELIYOR, BU JS ARACINDAN DEGIL -- yani bu araci YANILTMAK, GERCEK bir onay-gerekliligini ATLATMAZ, sadece YANLIS bir BILGILENDIRME-yorumu URETIR (orn. yanlis kisiye bildirim, ya da fazladan bildirim). (2) BASKA bir tuketici (orn. composite action.yml'de bir GATE olarak kullanimi) bu teslimde YOK ve VARLIGI dogrulanamadi -- spekulatif bir yukselme-zinciri KURMAK, somut KANIT OLMADAN confidence'i YUKSELTMEK icin YETERLI DEGIL. (3) Bu, bu oturumun onceki 'dusuk-riskli dogruluk sapmasi, GUVENLIK sinirina ULASMIYOR' kalibrasyon desenine (orn. base_base-std NatSpec tutarsizligi, confidence ~10) BENZER -- hint-tier'in ALT ESIGINE YAKIN ama MISSING_FILES de yok, confidence de >=15 cizgisinin HEMEN USTUNDE (18) -- TEKNIK OLARAK DOGRU bir gözlem olarak hint-tier'a GECIYOR, ama bagimsiz bir GUVENLIK bulgusu olarak REJECT. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._