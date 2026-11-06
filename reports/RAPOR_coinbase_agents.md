# Bug Bounty Raporu — coinbase_agents

**Tarih:** 2026-11-02 10:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/agents, AI agent skill/eklenti paket dagitim deposu, Python).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_agents/raw`
* **Engellenen/erişilemeyen adımlar:** Bu turda yalnizca README.md ve scripts/build-distributions.py geldi; gercek skills/*.md icerigi ve .github/workflows/*.yml (CI'da bu script'in kimin PR'inda, hangi yetkiyle calistirildigi) gelmedi., validate_selected_skill_links() yalnizca .md dosyalarindaki markdown linklerini tariyor; skills/ altindaki dosya agacinin kendisinde (md disi dosyalarda) sembolik link olup olmadigini KONTROL ETMIYOR gibi gorunuyor - bunu dogrulamak icin copy_tree()/shutil.copytree cagri zinciri ve CI is akisi gerekli.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* build-distributions.py ayrica guclu bir savunma iceriyor: copy_skills() secili her 'product' adini sikici regex ile (^[a-z0-9]+(-[a-z0-9]+)*$) dogruluyor, kok skill dizininin kendisinin sembolik link olmasini reddediyor, ve validate_selected_skill_links() markdown linklerinin SECILI skill'lerin KOKLERI disina CIKMASINI (path traversal via '../') engelliyor - bu TAM OLARAK path-traversal/zip-slip benzeri bir siniftan korunmak icin yazilmis, ama kapsamini '.md icindeki linkler'le sinirlamis, dosya agacindaki FIZIKSEL sembolik linkleri degil.
* scripts/build-distributions.py disinda kod YOK bu turda (README.md haric); diff'teki digerleri (SKILL.md, plugins/aerodrome.md, cli.md) salt dokumantasyon - prompt injection potansiyeli (bir AI agent'i yanlis yonlendirecek talimatlar) tasiyabilir ama bu klasik bir 'kod zafiyeti' degil, HackerOne kod-zafiyeti kapsamina net girmiyor; bu turda derinlemesine icerik analizi yapilmadi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 20 | REJECT | Istismar once zararli bir sembolik linkin repoya/PR'a girmesini ve bu script'in guvensiz bir checkout uzerinde CI'da calismasini gerektiriyor; is akisi dosyalari gelmedigi icin dogrulanamadi. | .github/workflows/*.yml |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._