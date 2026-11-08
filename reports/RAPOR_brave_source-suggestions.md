# Bug Bounty Raporu — brave_source-suggestions

**Tarih:** 2026-11-08 02:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/source-suggestions (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Python. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_source-suggestions/raw`
* **Engellenen/erişilemeyen adımlar:** `feed.json`'in NASIL uretildigi (yani Brave'in HANGI UPSTREAM servisinin RSS/Atom besLEMELERINI TARADIGINI VE `publish_time`/`publisher_id` alanlarini NASIL CIKARDIGINI) bu teslimin KAPSAMI DISINDA (AYRI bir repo) -- bu nedenle `publish_time`'IN GERCEKTEN yayincinin KENDI RSS besLEMESINDEN (`<pubDate>`/`<published>` ETIKETI) HAM olarak GELDIGI VARSAYIMI MANTIKLI (bu, standart RSS/Atom alan ADIDIR VE kod bunu HICBIR DOGRULAMA/PARSE ETME OLMADAN DOGRUDAN KULLANIYOR) ANCAK KESIN olarak bu REPO'NUN DISINDAKI bir bilesen TARAFINDAN bagimsiz DOGRULANAMADI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i -- gorunuse gore kucuk GUNCELLEMELER, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave News'in 'kaynak onerisi' (source suggestion) OZELLIGI icin yayinci-EMBEDDING'LERI VE benzerlik-MATRISI URETEN bir Python BATCH-is boru-hatti -- TOPLANAN makale BASLIKLARI/aciklamalari sentence-transformer MODELLERIYLE EMBEDDING'E CEVRILIYOR VE yayinci-CIFTLERI arasindaki benzerlik HESAPLANIYOR.
* utils.py::clean_source_similarity_file -- bu fonksiyonda IKI AYRI, DAHA ZAYIF kalite SORUNU GOZLEMLEDIM: (1) `if s_id not in sources_sim_data: sources_sim_data.pop(s_id, None)` -- bu, zaten DICT'TE OLMAYAN bir ANAHTARI 'pop' etmeye CALISIYOR (ANLAMSIZ/etkisiz-KOD, muhtemelen bir MANTIK-HATASI/yazim-HATASI, ANCAK `.pop(key, None)` GUVENLI OLDUGU icin bir ISTISNA FIRLATMIYOR); (2) `for index, suggestion in enumerate(sources_sim_data[s_id]): ... sources_sim_data[s_id].pop(index)` -- BIR LISTEYI UZERINDE YINELEME YAPARKEN DEGISTIRMEK (classic Python ANTI-pattern), bu da BAZI GECERSIZ/eslesmeyen oneri-GIRDILERININ YANLISLIKLA ATLANIP TEMIZLENMEMESINE yol ACABILIR -- bu, F1'den DAHA ZAYIF/SPEKULATIF bir bulgu (SADECE bir VERI-temizleme ADIMININ EKSIKSIZ olmamasi, DOGRUDAN bir GUVENLIK siniri IHLALI DEGIL), bu nedenle AYRI bir bulgu olarak DEGIL, bir GOZLEM olarak kaydedildi.
* SONUC: Bu oturumda TEK, GUCLU sekilde (GERCEK pandas KUTUPHANESI ile) DOGRULANMIS bir bulgu (F1) var -- `publish_time`/`publisher_id`'nin CSV-guvenli HALE GETIRILMEMESI, kimlik-dogrulamasiz bir RSS-kaynaginin Brave News'in kaynak-ONERI batch-ISINI KALICI olarak BOZABILMESINE VEYA BASKA bir yayincinin VERISINI KIRLETEBILMESINE yol ACIYOR.

## 📊 Bulgu F1: source-feed-accumulator.py::accumulate_articles(): 'publish_time' VE 'publisher_id' alanlari CSV-GUVENLI hale GETIRILMEDEN (tirnak/yeni-satir TEMIZLENMEDEN) ham-string-BIRLESTIRME ile CSV'YE YAZILIYOR -- kotu-niyetli/BOZUK bir RSS kaynaginin, source-similarity-matrix.py'nin TUM twice-weekly batch ISINI COKERTEBILMESINE VE/VEYA BASKA bir yayincinin EMBEDDING'INI KIRLETEBILMESINE yol ACAN CSV-enjeksiyonu
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-1236 (Improper Neutralization of Formula Elements in a CSV File) / CWE-20 (Improper Input Validation)
* **Stage 2 Confidence:** 38/100 — Stage1'in IDDIASINI BAGIMSIZ olarak YENIDEN URETTIM: `accumulate_articles()`'daki SANITIZE/non-sanitize ASIMETRISINI (title/description TEMIZLENIYOR, publish_time/publisher_id TEMIZLENMIYOR) SATIR SATIR DOGRULADIM, VE AYNI CSV-yazma MANTIGINI BAGIMSIZ bir Python SURECINDE CALISTIRARAK, `publish_time` alanina TEK bir `"` KARAKTERI ENJEKTE ETTIGIMDE GERCEKTEN `pandas.errors.ParserError: Expected 4 fields in line 2, saw 7` hatasinin URETILDIGINI KENDI TESTIMDE DE DOGRULADIM (stage1'in verdigi TAM senaryoyu TEKRARLADIM, AYNI SONUCU ALDIM). `source-similarity-matrix.py`'deki `articles_df = pd.read_csv(...)` cagrisinin GERCEKTEN try/except BLOGUNUN DISINDA, KORUMASIZ CALISTIGINI da satir-NUMARALARINI TAKIP EDEREK dogruladim -- bu, bir CRASH'IN GERCEKTEN TUM scripti (DONGUYU KIRARAK) SONLANDIRACAGI ANLAMINA geliyor, SADECE o LOCALE'i DEGIL.

BU BULGUYU CURUTMEYE CALISTIM: ASIL SORU, `article['publish_time']`'nin GERCEKTEN HAM/dogrulanmamis RSS `<pubDate>` ICERIGI MI OLDUGU, YOKSA Brave'in KENDI (bu REPO'NUN DISINDAKI) feed-URETME SERVISININ bunu ZATEN KATI bir ISO8601 FORMATINA NORMALLESTIRIP NORMALLESTIRMEDIGI -- EGER IKINCISI DOGRUYSA, `publish_time` PRATIKTE HICBIR ZAMAN bir `"` KARAKTERI ICEREMEZ VE bu bulgu TEORIK KALIR. Bu, bu teslimin KAPSAMI DISINDA (AYRI bir upstream repo) OLDUGU icin KESIN olarak COZULEMEDI -- stage1 bunu zaten DOGRU sekilde bir BLOKE-edilmis/dogrulanamayan VARSAYIM olarak ISARETLEMIS. BENZER sekilde, `publisher_id`'nin NE KADAR saldirgan-KONTROLLU OLDUGU da BELIRSIZ (muhtemelen Brave'in KENDI, DAHA SIKI KONTROLLU bir TANIMLAYICISI).

Bu BELIRSIZLIGE RAGMEN, kod-SEVIYESI defekt (title/description VE publish_time/publisher_id ARASINDAKI TUTARSIZ sanitizasyon, VE korumasiz `pd.read_csv` cagrisi) KESIN VE BAGIMSIZ olarak, GERCEK kutuphane DAVRANISIYLA dogrulandi -- bu, 'yapisal bir kod-defekti KESIN ONAYLANDI, ANCAK NIHAI GERCEK-dunya istismar-edilebilirligi teslim-DISI bir VARSAYIMA (upstream veri-FORMATI) BAGLI' kategorisine TAM olarak UYUYOR, bu oturumda DAHA ONCE BENZER sekilde DEGERLENDIRILEN bulgularla (orn. star-randsrv'nin rate-limit bulgusu) TUTARLI bir confidence SEVIYESINDE (38) raporlanmasi UYGUN.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._