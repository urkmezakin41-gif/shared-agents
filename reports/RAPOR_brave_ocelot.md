# Bug Bounty Raporu — brave_ocelot

**Tarih:** 2026-11-05 16:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/ocelot (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Python. Description: Dataset Collection, Training & Evaluation Code for Brave's Ocelot model.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_ocelot/raw`
* **Engellenen/erişilemeyen adımlar:** `src/training/data/pipeline.py` (4373-4433 ARASI, GORECELI olarak EN BUYUK dosya) VE `src/training/run.py`/`prepare_data.py`'nin TAM MANTIGI ZAMAN KISITI nedeniyle SATIR-SATIR incelenemedi -- SADECE `from_pretrained`/`torch.load`/`pickle`/`eval`/`exec`/`trust_remote_code` ICIN HEDEFLI bir grep YAPILDI (SIFIR SONUC/GUVENLI KULLANIM)., `src/data/api/` ALTINDAKI FastAPI SUNUCUSUNUN (chat_completions.py, backend.py) GERCEK dagitimda (deployment) HARICI AGA ACIK OLUP OLMADIGI bu REPO'NUN KAPSAMI DISINDA -- KOD, VARSAYILAN olarak `http://127.0.0.1:8000` (localhost) HEDEFLEDIGI VE `browser_automation/summarise_pages.py`'nin bu sunucuyu KENDI LOKAL Brave TARAYICISINA BAGLAMAK icin KULLANDIGI GOZLEMLENDI -- bu ikisi BIRLIKTE, SADECE Brave'in KENDI ML-arastirmacisinin KENDI GELISTIRME makinesinde CALISTIRDIGI bir YEREL VERI-TOPLAMA CIFTI OLDUGUNU GUCLU SEKILDE ima EDIYOR, DIS AGA ACIK bir PRODUKSIYON servisi DEGIL -- ANCAK bu, KESIN olarak DOGRULANAMAZ (altyapi/deployment KONFIGURASYONU bu teslimde YOK).

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki AYNI commit diff'i (requirements.txt BAGIMLILIK GUNCELLEMELERI -- litellm 1.93.2 -> 1.100.4 ONEMLI bir SURUM atlamasi, certifi/filelock/msgpack/tornado GUNCELLEMELERI) -- rutin BAGIMLILIK-GUNCELLEME, GUVENLIK acisindan NOTR/pozitif (litellm'in BUYUK surum ATLAMASI muhtemelen UPSTREAM GUVENLIK duzeltmelerini ICERIYOR).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in 'Ocelot' modeli icin VERI-TOPLAMA (web SAYFALARINI OZETLEME via Playwright+GERCEK Brave Dev BINARY'si), EGITIM (DPO/IPO/SFT) VE DEGERLENDIRME (LLM-judge KARSILASTIRMALI SKORLAMA) kod TABANI -- bu bir URETIM SERVISI DEGIL, bir ML-arastirma/egitim BORU-HATTI, bu nedenle tipik 'DIS saldirgan' TEHDIT MODELI buyuk olcude FARKLI/DAHA SINIRLI (cogu BILESEN, Brave'in KENDI arastirmacisinin KENDI makinesinde CALISTIRDIGI yerel ARACLAR).
* `src/data/api/` (FastAPI 'Ocelot data API') -- bir OpenAI-UYUMLU `/v1/chat/completions` ENDPOINT'I, ARKA PLANDA `litellm` ARACILIGIYLA GERCEK LLM SAGLAYICILARINA (bedrock/openai/vb.) 'chosen'/'rejected' COMPLETION'LAR ICIN CAGRI YAPIYOR -- bu, DPO-stili TERCIH-VERISI URETMEK icin TASARLANMIS, VARSAYILAN olarak `localhost:8000`'e BAGLI bir YEREL SUNUCU. `OpenAIRequest` pydantic MODELI `extra = 'ignore'` ile FAZLA alanlari SESSIZCE YOK SAYIYOR -- injection/type-confusion riski GOZLENMEDI.
* `services/backend.py::litellm_model_id()`/`_bedrock_litellm_model()`/`_ensure_bedrock_converse_route()` -- model-ADI/ARN ESLEME MANTIGI DIKKATLI YAZILMIS, STRING-manipulasyonu SADECE ONEK KONTROLU/EKLEME, komut-ENJEKSIYONU veya PATH-traversal YOLU YOK.
* `src/data/browser_automation/summarise_pages.py` -- Playwright ARACILIGIYLA GERCEK, YEREL olarak DERLENMIS bir Brave Dev BINARY'SINI BASLATIYOR; TUM YAPILANDIRMA (BRAVE_SRC, BRAVE_USER_DATA_DIR, OCELOT_AI_CHAT_SERVER_URL) YEREL ORTAM-DEGISKENLERINDEN GELIYOR -- DIS/saldirgan-kontrollu bir GIRDI YOK, bu SADECE bir GELISTIRICI aracidir.
* `src/data/resolve_brave_executable.py` -- SAF, YEREL bir DOSYA-YOLU cozumleme CLI ARACI, AG/komut-ENJEKSIYONU YOK.
* `src/evaluation/judge/llm_judge.py`/`judge_prompts.py` -- bir LLM-judge, SCRAPE EDILMIS WEB iceriginden TUREYEN EGITIM konusmalarini KARSILASTIRIYOR. TEORIK olarak, KOTU-NIYETLI bir web SAYFASI (eger scrape EDILIP EGITIM-VERISINE DAHIL EDILIRSE) judge'in SKORLAMASINI MANIPULE ETMEYE calisan bir prompt-injection ICEREBILIR -- ANCAK bu, bir VERI-KALITESI/model-ZEHIRLEME RISKI (ML EGITIM BORU-HATLARININ GENEL VE KACINILMAZ bir OZELLIGI, web-scrape EDILMIS VERI KULLANAN HERHANGI bir SISTEM icin GECERLI), bu REPO'YA OZGU bir KOD-DUZEYINDE guvenlik ACIGI DEGIL -- bulgu olarak SUNULMADI.
* `from_pretrained`/`torch.load`/`pickle`/`eval`/`exec`/`trust_remote_code` icin TUM teslimde GENIS-CAPLI grep YAPILDI -- `trust_remote_code=True` HICBIR YERDE GOZLENMEDI (bu bulunsaydi, HuggingFace model HUB'INDAN keyfi kod YURUTME RISKI OLUSTURURDU), NE `pickle` NE DE dogrudan `torch.load` CAGRISI BULUNDU (model YUKLEME STANDART, GUVENLI `from_pretrained()`/`PeftModel.from_pretrained()` ARACILIGIYLA).
* SONUC: Bu ML-arastirma/egitim BORU-HATTINDA, incelenen alanlarda (veri-toplama API'si, tarayici-OTOMASYONU, judge KODU, model-YUKLEME) odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._