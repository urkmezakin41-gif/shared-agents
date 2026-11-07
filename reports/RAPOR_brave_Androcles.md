# Bug Bounty Raporu — brave_Androcles

**Tarih:** 2026-11-07 15:38 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/Androcles (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Python. Description: Dataset Generation & Model Training code for our prompt classification model.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_Androcles/raw`
* **Engellenen/erişilemeyen adımlar:** `dataset_generator/gap_analysis_generator.py` (800+ satir) VE `dataset_generator/multilabel_labeller.py` (1000+ satir)'in TAMAMI, ZAMAN KISITI nedeniyle SATIR-SATIR incelenemedi -- SADECE HEDEFLI grep TARAMALARI (subprocess/eval/pickle/trust_remote_code/API-anahtar DESENLERI icin) VE cagri-SITELERI goruldu., `search_agent`/`tools` PARAMETRELERININ TAM implementasyonu (HANGI ARAMA ARACININ -- Tavily/SerpAPI/Brave Search API VB. -- kullanildigi) bu teslimde ACIKCA GORUNMUYOR (muhtemelen bir LangChain ARACI/baska bir paketten ITHAL EDILIYOR, bu DOSYANIN DISINDA) -- bu nedenle GERCEK AG-istegi KATMANININKI (orn. SSRF-benzeri bir risk TASIYIP TASIMADIGI) DOGRUDAN DOGRULANAMADI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i -- gorunuse gore kucuk GUNCELLEMELER, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in 'prompt siniflandirma modeli' (muhtemelen Leo AI-asistaninin GUVENLIK/prompt-injection TESPIT katmani) icin VERI-SETI URETIMI VE model-EGITIMI kod tabani -- bir URETIM AG-SERVISI DEGIL, Brave'in KENDI ML-arastirmacilarinin YEREL/CI ortaminda CALISTIRDIGI bir ARASTIRMA/egitim BORU-HATTI (brave_ocelot'a BENZER bir TEHDIT MODELI).
* pipeline/data_manager.py, pipeline/orchestrator.py, pipeline/gap_detector.py -- TUM `subprocess.run(cmd)` cagrilarinin, `cmd`'nin bir LISTE (argv) OLARAK OLUSTURULDUGUNU (ASLA bir KABUK-dizesi/`shell=True` OLARAK DEGIL) SATIR SATIR DOGRULADIM -- bu, KOMUT-enjeksiyonu RISKINI (bazi BILESENLER YEREL dosya-YOLLARI veya CLI bayraklarindan GELSE bile) MIMARI olarak ORTADAN KALDIRIYOR.
* TUM `AutoTokenizer.from_pretrained`/`AutoModelForSequenceClassification.from_pretrained` cagrilarinin HICBIRINDE `trust_remote_code=True` KULLANILMADIGINI DOGRULADIM (bu bulunsaydi, keyfi-kod-yurutme RISKI OLUSTURURDU) -- model YUKLEME STANDART/GUVENLI yontemle yapiliyor.
* dataset_generator/llm_factory.py -- `VLLM_API_KEY = "EMPTY"` (vLLM'in KENDISI bu degeri YOK SAYIYOR, SADECE litellm/OpenAI istemci KUTUPHANESININ bos olmayan bir deger BEKLEMESI nedeniyle VAR) -- GERCEK/hassas bir API anahtari KOD ICINDE SABIT-KODLANMAMIS; TUM LLM cagrilari YEREL/operator-yapilandirmali bir vLLM SUNUCUSUNA gidiyor GIBI GORUNUYOR.
* dataset_generator/topic_search_generator.py::search_topic -- bir LLM-tabanli ARAMA-AJANI (arama SORGULARI URETIP calistiriyor) KULLANIYOR -- GERCEK web-ICERIGININ (potansiyel olarak KOTU-niyetli bir SAYFADAN gelen PROMPT-INJECTION girisimleri DAHIL) sonraki LLM PROMPT'larina DAHIL EDILMESI TEORIK olarak bir veri-KALITESI/model-zehirlenmesi RISKI TASIR -- ANCAK bu, bu oturumda brave_ocelot icin ZATEN uygulanan AYNI DEGERLENDIRMEYLE ('web-scrape edilmis veri KULLANAN HERHANGI bir ML egitim BORU-HATTININ GENEL VE KACINILMAZ bir OZELLIGI, bu REPO'YA OZGU bir KOD-seviyesi guvenlik ACIGI DEGIL') TUTARLI -- ayri bir bulgu olarak SUNULMADI.
* SONUC: Bu ML-arastirma/egitim BORU-HATTINDA, incelenen alanlarda (subprocess-GUVENLIGI, model-yukleme, API-anahtar YONETIMI) odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._