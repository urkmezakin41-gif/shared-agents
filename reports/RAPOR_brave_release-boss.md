# Bug Bounty Raporu — brave_release-boss

**Tarih:** 2026-11-05 02:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/release-boss (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Python. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_release-boss/raw`
* **Engellenen/erişilemeyen adımlar:** GitHub profil 'display name' (closed_by.name) alaninin KABUL ETTIGI TAM karakter kumesinin (ozellikle `<`, `>`, `|`, `!` gibi Slack mrkdwn SENTAKS karakterlerini ICEREBILIP ICEREMEYECEGI) GitHub'in KENDI profil-dogrulama kurallari OLDUGU icin bu statik-analiz kapsaminda KESIN olarak DOGRULANAMADI -- bu, F1 bulgusunun GERCEK-saha tetiklenebilirligini SINIRLAYAN ana belirsizlik., Slack `chat.postMessage` API'sinin VARSAYILAN `mrkdwn` PARSE davranisinin (ozellikle `<!channel>`/`<!here>` ozel SENTAKSININ bir `text` parametresi ICINDE, BASKA bir formatting olmadan GERCEKTEN canli olarak ISLENIP ISLENMEYECEGI) canli bir Slack workspace'i GEREKTIRDIGI icin bu statik, pasif analiz kapsaminda DOGRULANAMADI -- static-analysis-only kural geregi canli test YAPILMADI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] pyproject.toml/uv.lock'taki `exclude-newer` degisikligi (1 hafta -> 3 gun) -- bu SADECE `uv` BAGIMLILIK-COZUMLEME penceresini AYARLAYAN bir TEDARIK-ZINCIRI HIJYEN ayari, bir GUVENLIK ACIGI DEGIL (daha KISA bir pencere, YENI-yayinlanan kotu-niyetli paketlerin tespit edilme SURESINI AZALTIYOR olsa da, bu bir YAPILANDIRMA TERCIHI, kod-defekti DEGIL).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in brave-browser/brave-ios/brave-core depolarinda kapanan issue/PR'lari TARAYIP eksik etiket/milestone durumunda GitHub kullanicilarina Slack UZERINDEN 'nagging' (hatirlatma) mesaji GONDEREN bir ic ADMINISTRATIF otomasyon botu. Teslim edilen TUM dosyalar (README.md, brave/config.py, brave/messages.py, brave/parsing.py, brave/slack.py, brave/test_parsing.py, brave/util.py, main.py, plot.py) satir-satir incelendi.
* `parsing.get_closed_issue()` -- PR GOVDE METNINDEN 'Fixes org/repo#123' veya 'Fixes https://github.com/org/repo/issues/123' KALIPLARINI CIKARIYOR; `fix_milestone_pr()` BU ciktiyi KULLANMADAN ONCE `if closed_repo_stub != 'brave/brave-browser': return` ILE SIKI bir ALLOWLIST KONTROLU uyguluyor -- BU, saldirgan-kontrollu bir PR govdesinin RASTGELE bir org/repo'ya ERISIM SAGLAMASINI ETKIN SEKILDE ONLUYOR; CURUTULMUS bir SSRF/keyfi-repo-erisimi hipotezi.
* `get_github_repo()`/`fix_milestone_prs()`/`get_pull_requests()` -- `repo_stub` parametresi HER ZAMAN `main.py`'den SABIT, hardcoded degerlerle (`brave/brave-core`, `brave/brave-browser`, `brave/brave-ios`) CAGRILIYOR, DIS/kullanici girdisi ICERMIYOR.
* `rate_limit_for_value()` -- GitHub API rate-limit TUKENMESINI onlemek icin uyku/bekleme MANTIGI, dogru UYGULANMIS, guvenlik acisindan TARAFSIZ.
* ReDoS hipotezi (parsing.py::close_regex/num_regex) ARASTIRILDI -- `(.+)\b` SONUNDA potansiyel backtracking VAR AMA PR govde METNI boyutu GitHub tarafindan ZATEN sinirlandirilmis (~65536 karakter) VE desen basit/tek-seviyeli (NESTED quantifier YOK) -- pratik bir DoS vektoru olarak DEGERLENDIRILMEDI, ODUL DEGERI YOK.
* `github_slack_map`'teki statik GitHub-kullanici-adi -> Slack-ID eslesmesi -- bu BIR CALISAN LISTESI, 'gizli bilgi' (secret) DEGIL, zaten PUBLIC GitHub profillerine karsilik GELEN dahili Slack kimlikleri -- hassasiyet derecesi DUSUK, AYRI bir bulgu olarak RAPORLANMADI.

## 📊 Bulgu F1: GitHub kullanici-kontrollu 'display name'/'login' alanlarinin, dogrulama/kacis-islemi (escaping) YAPILMADAN Slack mesaj metnine enterpole edilmesi (Slack mrkdwn/mention injection)
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-116 (Improper Encoding or Escaping of Output) -- Slack mrkdwn/mention injection
* **Stage 2 Confidence:** 42/100 — Stage1'in kod-seviyesi IDDIASINI (format_name/message_fn fonksiyonlarinin closed_by_login/closed_by_name degerlerini HICBIR kacis-islemi YAPMADAN Slack chat.postMessage'in `text` alanina ENTERPOLE ETTIGI) TEKRAR kod-okuyarak DOGRULADIM -- bu KESIN VE TARTISMASIZ.

STAGE1'DE KUCUK BIR DUZELTME: Bulgu basligi `closed_by_login` VE `closed_by_name`'i BIRLIKTE 'guvensiz' olarak CERCEVELEMIS, AMA bu IKISI AYNI RISK SEVIYESINDE DEGIL -- GitHub `login` (kullanici-adi) alani GitHub'in KENDI KISITLI formatina TABI (sadece alphanumeric + tire, bastaki/sondaki/ardisik tire YOK) -- bu alanda `<`, `>`, `!`, `|` GIBI Slack mrkdwn ozel karakterleri YAPISAL olarak MUMKUN DEGIL. GERCEK saldiri YUZEYI SADECE `closed_by_name` (GitHub profil 'display name'/'full name' ALANI) -- bu alan GitHub'da SERBEST-METIN, karakter KISITLAMASI YOK (herkese-acik bilgi: GitHub profil adlari rastgele Unicode ICEREBILIR, URL/username formatina TABI DEGILDIR).

IKI DIS-SISTEM-DAVRANISI HIPOTEZINI, CANLI TEST OLMADAN, KAMUYA ACIK, IYI-BILINEN API DAVRANISINA DAYANARAK DEGERLENDIRDIM (static-analysis-only kurali altinda CANLI DOGRULAMA YAPILAMADI, bu nedenle bu KESIN DEGIL AMA MAKUL bir temele DAYANIYOR): (1) GitHub profil 'name' alani -- herkese-acik BILGIYE GORE herhangi bir YAZDIRILABILIR Unicode karakteri (`<`, `>`, `!`, `|` DAHIL) KABUL EDIYOR, cunku sadece bir GORUNTU METNI, URL/tanimlayici olarak KULLANILMIYOR. (2) Slack `chat.postMessage` -- `mrkdwn` parametresi VARSAYILAN olarak `true`, VE `<!channel>`/`<!here>`/`<@USERID>` KOSELI-PARANTEZ sentaksi, `parse` parametresinin degerinden BAGIMSIZ olarak Slack'in KENDI mrkdwn ISLEYICISI tarafindan HER ZAMAN OZEL olarak taniniyor (bu, link-detection'dan AYRI bir mekanizma) -- bu nedenle metin icinde literal `<!channel>` GONDERMEK, VARSAYILAN ayarlarla GERCEKTEN bir kanal-geneli PING TETIKLER.

HER IKI VARSAYIM da KAMUYA ACIK DOKUMANTASYONLA TUTARLI VE MAKUL, ANCAK bu oturumun static-analysis-only KISITLAMASI altinda CANLI olarak DOGRULANAMADIGI icin confidence'i 'KESIN kod-defekti + COK DUSUK saldirgan-onkosulu (sadece bir GitHub hesabi + kendi actigi issue'yu kapatma) + MAKUL-AMA-DOGRULANMAMIS DIS-SISTEM davranisi' kategorisinde, 42'de SABITLEDIM -- bu oturumun SSRF-benzeri bulgularindan (45-52 araligi) biraz DAHA DUSUK CUNKU etki SADECE bir internal BILDIRIM mekanizmasina HASREDILMIS (kod-yurutme veya veri-sizintisi YOK), ama 'tamamen reddedilebilir/onemsiz' kategorisinin DE USTUNDE CUNKU saldirgan-onkosulu GERCEKTEN COK DUSUK VE etki (internal Slack kanalinda/DM'de mass-ping veya kilik-degistirilmis phishing linki) SOMUT bir SOSYAL-MUHENDISLIK riski.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._