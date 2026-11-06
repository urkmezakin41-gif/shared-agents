# Bug Bounty Raporu — base_skills

**Tarih:** 2026-11-03 08:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/skills (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: Python. Description: npx skills add base/skills.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_skills/raw`
* **Engellenen/erişilemeyen adımlar:** Bu scriptleri cagiran herhangi bir otomatik/sunucu-tarafi sarmalayici (orn. 'npx skills add' CLI'sinin kendisi, veya bir web tabanli 'skill olustur' akisi) teslim edilmedi -- bu nedenle init_skill.py'nin skill_name argumanini DOGRUDAN, dogrulanmamis kullanici girdisinden (bir guven sinirini asarak) cagiran bir yol olup olmadigi dogrulanamadi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, 'npx skills add base/skills' ile dagitilan Claude Code skill koleksiyonu (dokumantasyon/SKILL.md dosyalari + bir 'skill-creator' Python CLI araci). Son iki commit SADECE .md dosyalarinda (plugin-review skill'inin SKILL.md/references'lari, README, PR sablonu, base-mcp/wallet-mcp README/SKILL.md) -- calisan kod degisikligi yok, prompt/dokumantasyon metni degisiklikleri.
* F1 disinda, `package_skill.py`'nin zip olusturma mantigi (`skill_path.rglob('*')` + `zipf.write`) de incelendi: bu, bir skill klasorunu .skill (zip) dosyasina paketleyen bir CLI aracidir, zip'TEN CIKARMA (extraction) yapmiyor, bu nedenle klasik 'zip-slip' riski burada GECERLI DEGIL (o, zip ACARKEN olusur). Yine de, eger skill klasoru icinde disardaki bir dosyaya (orn. ~/.ssh/id_rsa) isaret eden kotu niyetli bir sembolik link varsa, `rglob('*')` + `is_file()` bu sembolik linki TAKIP EDER ve hedef dosyanin icerigini pakete gomer -- ancak bu, oncesinde bir insan kod incelemesinden (PR merge) gecmis olmasi gereken bir skill-klasoru icerigine bagli, dogrulanmis bir CI/guven-siniri senaryosu olmadan somut bir istismar yolu degil (onceki oturumda coinbase_agents/build-distributions.py'de aynen bu sinifta, aynen bu nedenle hint-tier olarak degerlendirilen bulguyla AYNI kalip).
* `quick_validate.py`: SKILL.md frontmatter'i icin SIKI bir allowlist (name/description/license/allowed-tools/metadata) + hyphen-case regex + uzunluk sinirlari (name<=64, description<=1024) + aci-ayrac (`<`/`>`) yasagi dogru uygulanmis -- YAML ayrismasi `yaml.safe_load()` ile yapiliyor (guvenli, `yaml.load()` degil) -- YAML deserialization saldirisi riski yok.
* SONUC: Dogrulanabilir ama cagiran-baglami eksik (missing_files) ve dusuk-etkili iki gozlem (F1: init_skill.py path-traversal-sekilli girdi dogrulamasi eksikligi; paketleme sirasinda sembolik link takip etme) disinda, HackerOne-raporlanabilir bir guvenlik acigi TESPIT EDILEMEDI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 20 | REJECT | Kod-okumasiyla DOGRULANABILIR gercek bir eksiklik (skill_name CLI argumani dizin-olusturmadan once dogrulanmiyor, dokumante edilen kisitlamalar kod icinde yok) -- ancak HackerOne-raporlanabilir bir guvenlik acigi barajini GECMIYOR: (1) Bu, skill-creator CLI'sini CALISTIRAN KISININ KENDI makinesinde KENDI CLI argumanini yazdigi bir yerel gelistirici araci -- bir saldirganin baska bir KULLANICIYI veya SUNUCUYU bu yolla etkileyebilecegi bir cagiran-zincir (otomatik/uzaktan/web-tabanli bir 'skill olustur' akisi) teslim edilen veride YOK. (2) Kendi komut satirina kendi `../` yazan bir kullanicinin kendi dosya sistemini etkilemesi bir yetki yukseltme veya baska bir taraf GUVENLIK IHLALI degil. (3) 'npx skills add base/skills' ile SON KULLANICIYA dagitilan asil urun bu creator-tooling degil, skill icerigidir (SKILL.md + destekleyici dosyalar) -- bu nedenle bu script zaten genis saldiri yuzeyinin disinda. Confidence=20, hint-tier'e yonlendiriliyor (savunma-katmani onerisi olarak kaydedildi, tam rapor/Telegram bildirimi seviyesinde degil). |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._