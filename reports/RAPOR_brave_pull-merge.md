# Bug Bounty Raporu — brave_pull-merge

**Tarih:** 2026-11-05 07:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/pull-merge (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: LLM Capabilities for your pull-requests.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_pull-merge/raw`
* **Engellenen/erişilemeyen adımlar:** `action.cjs`'in TAM icerigi bu teslimde YOK -- SADECE varsayilan config degerlerine yapilan KUCUK bir diff (3-4 satir) var. Bu dosya, HANGI PR'in 'renovate' VEYA 'dependabot' TIPINDE OLDUGUNU belirleyip `getRenovatePatch`/`getDependabotPatch`'i CAGIRMA KARARINI VEREN DISPATCHER MANTIGINI icermesi GEREKEN TAM dosya -- F1 bulgusunun GERCEK-saha tetiklenebilirligi TAMAMEN bu EKSIK dosyanin icerigine BAGLI (asagida detayli ACIKLANDI).

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] action.cjs/pnpm-lock.yaml/pnpm-workspace.yaml'daki iki commit diff'i -- SADECE varsayilan filterdiff_args/model ADLARI GUNCELLEMESI VE rutin brace-expansion bagimlilik GUNCELLEMESI, guvenlik acisindan NOTR.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, GitHub PR'lerini LLM (OpenAI/Anthropic/Bedrock) ile 'aciklayan' VE SONUCU bir YORUM OLARAK GONDEREN (submitReview.js) VEYA PR ACIKLAMASINI GUNCELLEYEN (subtleSubmitReview.js) bir GitHub Action. ONEMLI YAPISAL GOZLEM: bu bot HICBIR ZAMAN bir ONAYLAYICI/REDDEDICI GITHUB REVIEW EYLEMI (APPROVE/REQUEST_CHANGES) GERCEKLESTIRMIYOR -- SADECE METIN-TABANLI bir YORUM/ACIKLAMA-GUNCELLEMESI YAPIYOR. Bu, HERHANGI bir prompt-injection senaryosunun NIHAI ETKISINI 'botun KENDI yorumunun ICERIGINI MANIPULE ETME' ile SINIRLIYOR -- branch-protection/CI-BYPASS veya otomatik-MERGE riski GOZLENMEDI.
* `filterdiff.js` -- `spawn('filterdiff', realArgs)` ARGV-DIZISI FORMUNDA (shell=true DEGIL), PR diff ICERIGI stdin UZERINDEN PIPE EDILIYOR (komut SATIRINA ENTERPOLE EDILMIYOR) -- saldirgan TAM KONTROLDEKI diff ICERIGINE RAGMEN komut-enjeksiyonu MUMKUN DEGIL.
* `getPatch.js`'in FALLBACK YOLUNDAKI `execSync` cagrilari (STRING-interpolasyonlu, shell-yorumlanan) `owner`/`repo` (GitHub'in KENDI repo-SLUG format KISITLAMASINA TABI, shell meta-karakteri ICEREMEZ) VE `baseSha`/`headSha` (HER ZAMAN 40-karakter hex git SHA, AYNI SEKILDE KISITLI) KULLANIYOR -- GORUNUSTE KOTU bir KOD-KALIBI (string-execSync) OLSA DA, DEGER-UZAYI DIS SISTEMLER (GitHub, git) TARAFINDAN ZATEN KISITLANDIGI icin GERCEK bir komut-enjeksiyonu YOLU DEGIL.
* `getDependabotPatch.js` AYNI 'PR-govdesinden-link-cikarma' KALIBINI KULLANIYOR AMA sonucu `fetch()`'e GECIRIYOR (F1'deki GIBI) -- AYNI potansiyel SSRF/LLM-girdi-ele-gecirme deseni, AYNI GATING-BELIRSIZLIGINE TABI (action.cjs GOZLENEMEDI). AYRI bir bulgu olarak SAYILMADI, F1 ILE AYNI KOK-NEDEN/AYNI onerilen DUZELTME GECERLI.
* `openaiExplainPatch.js`/`anthropicExplainPatch.js`/`bedrockExplainPatch.js` -- hepsi SISTEM-PROMPT'u (SABIT, kod-icinde TANIMLI) KULLANICI-GIRDISINDEN (patchBody) AYRI TUTUYOR, max_tokens/stop_reason ISLEME MANTIGI DIKKATLI ('truncated review never posted') -- bu DOSYALARIN KENDI MANTIGINDA BASKA bir defekt GOZLENMEDI.
* `getConfig.js`/`getProperties.js` -- repo config/property OKUMA, BASIT try/catch ILE hata-TOLERANSLI, injection YOLU YOK.
* SONUC: Tek aday bulgu (F1, getRenovatePatch.js ve benzer sekilde getDependabotPatch.js), action.cjs'teki EKSIK dispatcher MANTIGI nedeniyle ORTA-duzey confidence ile RAPORLANIYOR.

## 📊 Bulgu F1: getRenovatePatch.js: PR govde-metninden cikarilan dogrulanmamis bir URL'nin, LLM'e beslenen icerigi GETIREN bir fetch() hedefi olarak kullanilmasi (SSRF + LLM-girdisi-ele-gecirme)
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-918 (Server-Side Request Forgery) birlesik CWE-74/CWE-1427 (prompt injection enablement)
* **Stage 2 Confidence:** 40/100 — Stage1'in kod-seviyesi IDDIASINI TEKRAR kod-okuyarak DOGRULADIM -- `getRenovatePatch.js`'in `link` degiskeni, GERCEKTEN PR'in KENDI govde-METNININ 5. satirindan (pipe-ayrilmis TABLO formatinda), HICBIR HOST-allowlist VEYA SIKI format-DOGRULAMASI OLMADAN CIKARILIYOR VE `fetch()`'in TABANI olarak KULLANILIYOR; bu fetch'in CEVABI DOGRUDAN LLM'e 'PR diff' OLARAK GONDERILEN METNE DONUSUYOR. `getDependabotPatch.js`'in de AYNI DESENI TEKRARLADIGINI BAGIMSIZ olarak DOGRULADIM.

CURUTMEYE CALISTIGIM AMA COZEMEDIGIM ANA SORU: bu IKI fonksiyonun action.cjs TARAFINDAN HANGI KOSULDA CAGRILDIGI -- bu teslimde action.cjs'in SADECE varsayilan-config DIFF'i VAR, DISPATCHER MANTIGININ TAMAMI YOK. Dosya-adlandirma KALIBI (`getPatch.js` [type:'simple'], `getDependabotPatch.js`, `getRenovatePatch.js`) bir TYPE-BAZLI dispatch OLDUGUNU GUCLU SEKILDE ima EDIYOR, AMA bu dispatch'in `pull_request.user.login === 'renovate[bot]'` GIBI SAHTELENEMEZ bir bot-KIMLIK kontrolune mi, YOKSA PR BASLIGI/govde-SEKLINE bakan DAHA ZAYIF bir KALIP-eslestirmeye mi DAYANDIGI BELIRLENEMEDI. `submitReview.js`'teki MEVCUT, ZATEN SAGLAM bot-kimlik-DOGRULAMA DESENI (`msg.author?.__typename === 'Bot'`) bu PROJENIN GENEL OLARAK bot-kimligini DOGRU AYIRT ETMEYE ONEM VERDIGINI GOSTERIYOR, bu da action.cjs'in de BENZER bir SIKILIKTA kontrol UYGULADIGI YONUNDE HAFIF bir SINYAL -- AMA bu, DOGRULANAMAYAN bir CIKARIM, KANIT DEGIL.

Bu BELIRSIZLIK, confidence'i SINIRLAYAN TEK VE ANA FAKTOR. Yapisal KOD-defekti KENDI BASINA KESIN VE (eger TETIKLENEBILIRSE) ETKISI CIDDI (saldirganin LLM'e GONDERILEN 'PR diff' metninin TAMAMINI KEYFI olarak KONTROL ETMESI, botun KENDI GUVENLIK-incelemesi YORUMUNU/PR-aciklamasini MANIPULE ETMESI) -- bu nedenle bu oturumun 'yapisal defekt KESIN, GATING/DIS-bilesen DOGRULANAMADI' kategorisindeki BULGULARLA (constellation-processors 45, pagegraph-crawl 52, brave-variations 32) KARSILASTIRILABILIR bir SEVIYEDE, 40'ta SABITLEDIM.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._