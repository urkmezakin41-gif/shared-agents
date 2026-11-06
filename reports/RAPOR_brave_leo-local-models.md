# Bug Bounty Raporu — brave_leo-local-models

**Tarih:** 2026-11-06 12:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/leo-local-models (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Python. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_leo-local-models/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki commit diff'i -- (1) bir model icin lisans/NOTICE dosyalarinin EKLENMESI (NVIDIA Open Model License) VE (2) 'license-reviews' etiketi ICIN Brave'in KENDI license-reviewer EKIBINI TAG'LEYEN bir GitHub Actions is akisi EKLENMESI -- ikisi de VERI/surec DEGISIKLIGI, kod-DAVRANIS degisikligi DEGIL. Ikinci is akisini (`.github/workflows/tag-license-reviewer-team-for-sanctions-compliance.yml`) GUVENLIK acisindan ayrica inceledim: `pull_request`/`labeled` tetikleyicisi KULLANIYOR, `actions/github-script` ICINDE SADECE SABIT/statik bir yorum METNI YAZIYOR ('@brave/license-reviewer...'), HICBIR PR-BASLIGI/govdesi/etiket-ADI gibi SALDIRGAN-kontrollu veri script ICERIGINE veya BIR KABUK komutuna ENJEKTE EDILMIYOR (`context.issue.number` SADECE bir SAYI) -- bu nedenle GitHub Actions script-injection SINIFI bir ACIK YOK, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in Leo AI-asistaninin YEREL (on-device) modellerini (EmbeddingGemma, Nemotron Speech Streaming) VE bunlara eslik eden METADATA'yi (model-info.pb) TAKIP EDEN bir depo -- esas olarak LISANS/model-DOSYASI YONETIMI VE bir TEK gelistirici-ARACI script'inden OLUSUYOR, bir calisan AG SERVISI veya saldirgan-ERISILEBILIR bir calisma-ZAMANI BILESENI DEGIL.
* tools/generate_passage_embeddings_model_info.py -- SATIR SATIR incelendi: bu, bir GELISTIRICININ/CI'nin KENDI YEREL dosya SISTEMINDEKI bir 'model dir' uzerinde CALISTIRDIGI bir CLI araci (protobuf `ModelInfo`/`PassageEmbeddingsModelMetadata` mesajlarini `model-info.json`'dan URETIYOR). Girdi (`model_dir` CLI argumani, `model-info.json` ICERIGI) TAMAMEN YEREL/gelistirici-KONTROLLU -- uzak/saldirgan-KONTROLLU HICBIR girdi KAYNAGI YOK (AG cagrisi, HTTP sunucusu, kullanici-YUKLEMESI VB. YOK). `discover_additional_files()` SADECE ZATEN VAR OLAN model-dizinindeki dosyalari LISTELIYOR (saldirgan-saglanan bir YOL ILE path-traversal RISKI YOK, CUNKU `model_dir` ZATEN GUVENILIR CALISTIRICI TARAFINDAN SAGLANAN bir ARGUMAN).
* tools/proto_gen/components/optimization_guide/proto/*_pb2.py -- bunlar `protoc` TARAFINDAN OTOMATIK URETILEN protobuf BINDING dosyalari (Chromium'un KENDI .proto TANIMLARINDAN VENDOR edilmis) -- EL-YAZISI mantik ICERMIYOR, bu nedenle guvenlik-ILGILI bir DEGERLENDIRMEYE KONU OLAMAZ.
* SONUC: Bu depo, saldirgan-ERISILEBILIR hicbir ag-servisi, kullanici-girdisi-isleyen BILESEN VEYA ozel is-mantigi ICERMIYOR -- SADECE yerel gelistirici-araci kod VE otomatik-uretilen protobuf BINDING'leri. Odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI, rapor TEMIZ olarak dispatch edilmeli.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._