# Bug Bounty Raporu — brave_brave-variations

**Tarih:** 2026-11-05 03:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/brave-variations (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Resources to compile, publish and inspect the variations seed file.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_brave-variations/raw`
* **Engellenen/erişilemeyen adımlar:** `find_outdated_studies.ts --output <file>` ile uretilen Slack mrkdwn JSON payload'inin HANGI MEKANIZMAYLA (incoming webhook, ayri bir CI adimi VB.) GERCEKTEN Slack'e GONDERILDIGI bu teslimde YOK -- bu dosyanin KENDISI SADECE bir JSON uretiyor, GONDERIM ADIMI teslim kapsaminda DEGIL. ANCAK `type: 'mrkdwn'` block YAPISININ KENDISI, Slack Block Kit spesifikasyonunda ACIKCA mrkdwn-OLARAK-ISLE anlamina GELDIGI icin, bu belirsizlik sadece 'GONDERIM YONTEMI' ile SINIRLI, 'ISLENIP ISLENMEYECEGI' ile DEGIL.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] studies/*.json5 icerigindeki feature-flag KONFIGURASYON degisiklikleri (2 commit diff) -- SADECE VERI, kod-mantigi degisikligi YOK, guvenlik acisindan NOTR.
* [ÖDÜL DEĞERİ YOK - ATLANDI] `readStudiesAtRevision()`'daki `revision` parametresinin execSync'e enterpolasyonu ICIN bir command-injection HIPOTEZI olusturuldu AMA CURUTULDU: fonksiyon, `revision`'i KULLANMADAN ONCE `/^[a-z0-9]+$/.test(revision) && revision !== 'HEAD'` ile SIKI bir ALLOWLIST kontrolunden GECIRIYOR (satir 3065) -- shell meta-karakterleri (`;`, `$`, backtick, boşluk, tirnak) bu regex'ten GECEMEZ, bu nedenle execSync'e ULASAN deger ZATEN GUVENLI. Ayni fonksiyondaki `file` dongu-degiskeni de kullanilmadan once `validateName()` (ayni GUVENLI allowlist) ile FILTRELENIYOR.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in A/B test/Finch 'variations seed' dosyasini DERLEYEN, imzalayan VE inceleme ARACLARINI (CLI komutlari + bir React web GORUNTULEYICI) BARINDIRAN bir repo -- feature-flag ROLLOUT altyapisinin KALBI, bu nedenle critical severity ile SCOPE'TA.
* `crypto/crypto_util.go` -- ECDSA P-256 + SHA-256 ile seed imzalama, `crypto/rand` KULLANIMI DOGRU, standart VE guvenli bir uygulama -- kriptografik zayiflik BULUNAMADI.
* `study_validation.ts`/`seed_validation.ts` -- study/experiment/feature isimleri SIKI bir allowlist regex'le (`^[0-9a-zA-Z ._-]+$`) KISITLANIYOR; forcing_flag lowercase-zorunlulugu, probability_weight toplaminin 100 olmasi, filter cakismasi KONTROLLERI VB. hepsi dogru UYGULANMIS -- ANCAK bu, PR-incelemesinden GECEN icerige uygulanan bir LINT-GATE, dogrudan dis-saldirgan ERISIMI OLAN bir sinir DEGIL.
* `src/web/app/` (React web goruntuleyici) -- `sanitizeUrl()` (yerel, basit allowlist: SADECE `https://` ile BASLAYAN URL'lere IZIN VERIYOR, aksi halde `#`) TUM kullanici-kontrollu href'lerde (feature link, study config URL) DOGRU SEKILDE UYGULANMIS -- `javascript:`/`data:` scheme XSS'i ETKIN SEKILDE ENGELLIYOR. `maybeHighlight()`'in arama-vurgu MANTIGI React JSX `{text}` COCUKLARI ile RENDER EDILIYOR (otomatik HTML-escape) -- `dangerouslySetInnerHTML` HICBIR YERDE KULLANILMAMIS, DOM-tabanli XSS taramasi (grep: innerHTML/dangerouslySetInnerHTML/eval/document.write) TUM teslimde SIFIR SONUC VERDI.
* `study_processor.ts`'teki arama-filtresi (`StudyFilter.search` setter) -- kullanici arama METNINI bir RegExp'e DONUSTURMEDEN ONCE `value.replaceAll(/\W/g, '')` ile TUM ozel karakterleri SILIYOR -- ReDoS VE regex-injection riskini ETKIN SEKILDE ORTADAN KALDIRIYOR.
* `url_utils.ts::getGriffinUiUrl(study)` -- `study` parametresi `encodeURIComponent` ile KACIRILMADAN bir query-string'e enterpole EDILIYOR (digger URL-olusturucu fonksiyonlardan FARKLI olarak) -- ANCAK sabit `https://griffin.brave.com/?seed=UPSTREAM&search=` ONEKI her zaman path-ayiricidan ONCE geldigi icin HOST-confusion/scheme-degisikligi MUMKUN DEGIL; EN KOTU durum query-string'e EK parametre ENJEKTE EDILMESI (kendi domain'i uzerinde, dusuk-etki) -- ODUL DEGERI TASIMAYACAK KADAR DUSUK, AYRI bir bulgu olarak RAPORLANMADI.
* `diff_strings.ts` -- gecici dosya yollari TAMAMEN yerel-uretilmis (`os.tmpdir()` + `mkdtemp` + sabit dosya-adi KALIPLARI), `execAsync`'e giden shell komutunda HICBIR disaridan-gelen deger YOK -- guvenlik acisindan TEMIZ.

## 📊 Bulgu F1: GitHub PR-yazari 'display name' alaninin, kacis-islemi YAPILMADAN bir Slack mrkdwn block'una enterpole edilmesi
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-116 (Improper Encoding or Escaping of Output) -- Slack mrkdwn injection
* **Stage 2 Confidence:** 32/100 — Kod-seviyesi IDDIAYI TEKRAR kod-okuyarak DOGRULADIM -- `findPrAuthor()`'un `name` (GitHub display-name, serbest-metin) alanini KACISSIZ SEKILDE `${login} (${name})` OLARAK birlestirdigi VE `toSlackPayload()`'in bunu ACIKCA `type: 'mrkdwn'` OLARAK ISARETLENMIS bir Slack Block Kit metnine ENTERPOLE ETTIGI KESIN. Ayrica stage1'in `readStudiesAtRevision()` icin CURUTTUGU command-injection HIPOTEZINI de BAGIMSIZ olarak Python regex testiyle DOGRULADIM: `/^[a-z0-9]+$/` deseni, `; rm -rf /`, `a$(whoami)`, bosluk-iceren degerler DAHIL TUM shell meta-karakteri icerebilecek girdileri REDDEDIYOR -- bu CURUTME GECERLI VE DOGRU.

F1'IN GERCEK-SAHA tetiklenebilirligini SINIRLAYAN, stage1'in TAM OLARAK VURGULAMADIGI EK bir friksiyon katmani BULDUM: `findOutdatedStudies()`, bir dosyayi SADECE (a) `max_version` filtresi TANIMLI DEGILSE VE (b) `isWithinReviewWindow()` SONUCU `lastModified < cutoff` (VARSAYILAN 3 AY ONCE) ISE 'outdated' olarak RAPORLUYOR -- yani saldirganin PR'inin SADECE MERGE EDILMESI YETMIYOR, AYRICA (1) o dosyanin saldirganin PR'inden SONRA BASKA HICBIR commit ile GUNCELLENMEMIS OLMASI (cunku `getLastCommit()` SADECE o dosyanin EN SON commit'ini ALIYOR, `findPrAuthor` da SADECE o commit'in PR'ini ARIYOR) VE (2) EN AZ 3 AY GECMESI GEREKIYOR. Bu, saldiriyi 'HEMEN TETIKLENEBILIR' olmaktan 'YAVAS, DOLAYLI VE KISMEN saldirganin KONTROLU DISINDA (baska birinin o dosyayi GUNCELLEMEMESINE BAGLI)' bir SENARYOYA TASIYOR.

BUNA KARSILIK, release-boss'taki BENZER bulgudan FARKLI olarak, burada Slack'in bu metni mrkdwn OLARAK ISLEYECEGI (`type: 'mrkdwn'` ACIKCA BELIRTILDIGI icin) HICBIR TAHMIN/belirsizlik ICERMIYOR -- bu YONDEN DAHA KESIN.

IKI FAKTORU BIRLIKTE TARTARAK: kod-defekti KESIN VE mrkdwn-render BELIRSIZLIGI YOK (lehte), AMA saldirgan-ONKOSULU (PR-inceleme SURECINDEN GECME + 3-AY BEKLEME + SON-COMMIT OLMA SARTI) release-boss'tan ONEMLI OLCUDE DAHA YUKSEK VE DAHA AZ PRATIK/cazip bir saldiri SENARYOSU OLUSTURUYOR (ALEYHTE). Bu nedenle confidence'i release-boss'un 42'sinden DAHA ASAGIDA, 32'de SABITLEDIM.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._