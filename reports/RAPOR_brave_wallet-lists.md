# Bug Bounty Raporu — brave_wallet-lists

**Tarih:** 2026-11-05 01:43 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/wallet-lists (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Manages custom token lists for Brave Wallet.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_wallet-lists/raw`
* **Engellenen/erişilemeyen adımlar:** CoinGecko'nun KENDI public listing/submission surecinin tam olarak ne kadar KATI dogrulandigi (ozellikle 'cardano' platform adres alaninin FORMAT acisindan ne kadar SIKI KISITLANDIGI) bu teslimde DOGRULANAMADI -- bu, asagidaki F1 bulgusunun GERCEK-SAHA tetiklenebilirligini etkiliyor ama CoinGecko'nun KENDI altyapisi bu kapsamin DISINDA.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] data/v1/coingecko-top5000.json ve build/coingecko-ids.json'daki COK SAYIDA token-listesi EKLEME/CIKARMA/GUNCELLEME commit diff'i -- bunlar SADECE OTOMATIK GUNCELLENEN VERI dosyalari (gunluk cron-job ciktisi), herhangi bir KOD-MANTIGI DEGISIKLIGI ICERMIYOR, guvenlik acisindan NOTR.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Wallet'in token listelerini (CoinGecko evreni, Coinbase/Sardine on-ramp destegi, OFAC yaptirim listeleri, chainlist.json) GUNLUK bir CI/Jenkins cron-job ILE OLUSTURAN bir build-pipeline reposu. Teslim edilen TUM kaynak dosyalar (README.md, eslint.config.ts, scripts/coingecko-universe.ts, scripts/index.ts, scripts/lib/coingecko.ts, scripts/util.ts) satir-satir incelendi; data/v1/*.json ve build/*.json commit diff'leri SADECE otomatik veri GUNCELLEMESI (odul degeri yok).
* `getTokenInfoFromChain()` -- CoinGecko'nun verdigi kontrat ADRESI, SABIT (env-degiskeninden gelen) bir RPC URL'YE `eth_call` PARAMETRESI olarak gonderiliyor -- BU bir SSRF DEGIL (hedef HOST her zaman operator-kontrollu RPC saglayicisi, adres SADECE CAGRI PARAMETRESI).
* `nearToEvmAddress()` -- keccak256+EIP-55 checksum donusumu DOGRU UYGULANMIS, kriptografik hata YOK.
* `fetchGitHubRepoTopLevelFiles()`/`fetchGitHubFileContent()` -- repoOwner/repoName/branch PARAMETRELERI GENEL/yeniden-kullanilabilir SEKILDE yazilmis OLSA DA, bu TESLIMDE SADECE SABIT, HARDCODED degerlerle (`brave-intl`/`ofac-sanctioned-digital-currency-addresses`/`lists`) CAGRILIYOR -- `API_AUTH_TOKEN_GITHUB` secret'i, DEGISKEN/saldirgan-kontrollu bir hedefe SIZDIRILAMIYOR.
* `addSupportedCoinbaseTokens()`/`addSupportedSardineCurrencies()`/`generateChainList()` -- TUMU SABIT URL'lere fetch yapiyor, PARAMETRE ENTERPOLASYONU YOK, guvenlik acisindan TEMIZ.
* `isBlacklisted()`/blacklist.json KONTROLU -- adresler lowercase NORMALIZE EDILEREK KARSILASTIRILIYOR, case-sensitivity BYPASS riski YOK (EVM adresleri icin lowercase tutarli; Solana/Cardano zaten case-collision YOK).
* `writeUniverseJson()` -- tmp-dosyaya YAZIP ATOMIK rename ile TASIMA pattern'i, YARIM-YAZILMIS/bozuk veri dosyasi RISKINI dogru SEKILDE ONLUYOR.

## 📊 Bulgu F1: Guvenilmeyen ucuncu-taraf (CoinGecko) veri alanlarinin dogrulanmadan outbound fetch() URL'lerine enterpole edilmesi (build-time, sinirli-etki SSRF-benzeri davranis)
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** N/A
* **Zafiyet Sınıfı (CWE):** CWE-918 (Server-Side Request Forgery) / CWE-20 (Improper Input Validation) -- ZAYIFLATILMIS FORM
* **Stage 2 Confidence:** 48/100 — Stage1'in 'teorik path-traversal' notunu BAGIMSIZ olarak Node URL parser ile SOMUT bicimde DOGRULADIM VE Stage1'in degerlendirdiginden daha CIDDI oldugunu BULDUM: `getTokenInfoFromCardanoRegistry(address)`'teki `address` degerine 6 adet `../` segmenti EKLEYINCE (`../../../../../../some-other-org/some-other-repo/main/anyfile`), `new URL(...).pathname` TAMAMEN `/some-other-org/some-other-repo/main/anyfile.json` OLUYOR -- yani `mappings/` ALT-DIZININDEN DEGIL, `cardano-foundation/cardano-token-registry` REPOSUNDAN DA TAMAMEN CIKILIP raw.githubusercontent.com UZERINDEKI HERHANGI BIR PUBLIC repo/branch/path'e ULASILABILIYOR -- bu SADECE 'teorik' degil, SOMUT VE TEKRARLANABILIR.

BUNU ONEMLI KILAN KRITIK EK-GOZLEM (stage1'de EKSIK): `name`/`coingeckoId` alanlari ZATEN DOGRUDAN CoinGecko'nun KENDI (crowdsourced, herkesin kontrol EDEBILECEGI) coin-listing VERISINDEN geliyor VE HICBIR BAGIMSIZ DOGRULAMADAN GECMIYOR -- ANCAK `symbol`/`decimals` alanlari Cardano zinciri ICIN SADECE VE SADECE bu Cardano Token Registry fetch'inin SONUCUNA BAGLI (diger zincirlerdeki gibi bir on-chain RPC coklu-dogrulama YOK, CARDANO icin RPC URL'si bos string VE kod akisi dogrudan getTokenInfoFromCardanoRegistry'ye GIDIYOR -- bunu kod-okuma ile DOGRULADIM: satir 1821 `if (chainId === ChainId.CARDANO) return await getTokenInfoFromCardanoRegistry(address);`, ve sonrasinda satir 2048-2052'de bu symbol/decimals DOGRUDAN, baska bir CAPRAZ-KONTROL OLMADAN sonuc objesine YAZILIYOR). Bu, Cardano zinciri ICIN 'bagimsiz bir ucuncu-taraf kayit-defterinden dogrulama' SAGLAMAYI AMACLAYAN TEK mekanizmanin, path-traversal ILE TAMAMEN BYPASS EDILEBILDIGI anlamina geliyor -- saldirgan, CoinGecko'ya 'cardano' platform ADRES ALANINA bir traversal-PAYLOAD KOYARAK, KENDI SECTIGI ({"ticker":{"value":"USDC"},"decimals":{"value":6}} GIBI) ICERIGI barindiran HERHANGI bir PUBLIC GitHub dosyasina YONLENDIREBILIR VE boylece Brave Wallet'in GUNLUK yayinlanan, kullanicilara DAGITILAN (README.md'de ACIKCA belirtildigi gibi: haftalik Jenkins cron -> go-updater -> TUM Brave tarayicilarina) VARSAYILAN token listesine, SAHTE bir sembol/decimal CIFTIYLE, kendi-sectigi bir Cardano asset'i EKLEYEBILIR -- bu, kullanicilari KANDIRMAYA yonelik bir TOKEN-SPOOFING/phishing-enablement vektoru (orn. kotu niyetli bir token'in cuzdanda 'USDC' gibi GORUNMESI).

CURUTMEYE CALISTIGIM AMA BASARAMADIGIM ITIRAZLAR: (1) 'Host zaten SABIT, gercek SSRF degil' -- DOGRU AMA ETKISIZ: asil GUVENLIK SINIRI burada 'hangi HOST'a gidiliyor' degil, 'Cardano REGISTRY'NIN KENDI VETTING SURECI BYPASS EDILEBILIYOR MU' -- VE CEVAP KESIN OLARAK EVET. (2) 'Saldirgan zaten CoinGecko uzerinde coin.name'i KONTROL EDEBILIYOR, bu YENI bir sey EKLEMIYOR' -- KISMEN DOGRU AMA EKSIK: name ZATEN guvenilmez OLABILIR AMA symbol/decimals ozellikle Cardano icin BAGIMSIZ-DOGRULAMA ile KORUNMASI AMACLANAN alanlar -- bu KORUMA TAM OLARAK BYPASS EDILIYOR.

CONFIDENCE'I SINIRLAYAN FAKTOR: CoinGecko'nun KENDI coin-listing/submission SURECININ 'cardano' platform adres ALANINA HANGI FORMAT KISITLAMALARINI (varsa) UYGULADIGI bu teslimde DOGRULANAMADI -- EGER CoinGecko taraf, bu alani Cardano asset-ID formatina (SIKI alphanumeric/hex regex) ONCEDEN KISITLIYORSA, `../` KARAKTERLERI zaten CoinGecko SEVIYESINDE REDDEDILIR VE bu ZINCIR hic TETIKLENEMEZ -- bu DIS/harici bir SISTEMIN davranisina BAGLI VE bu kapsamda TEST EDILEMEDI. Bu nedenle confidence'i, bu oturumda 'yapisal defekt KESIN AMA nihai GERCEK-DUNYA tetiklenebilirligi teslim-KAPSAMI-DISI bir ALTYAPI/SISTEME BAGLI' kategorisine giren ONCEKI bulgularla (constellation-processors 45, slim-list-lambda 50, pagegraph-crawl 52) AYNI SEVIYEDE, 48'de SABITLEDIM -- biraz daha YUKSEK CUNKU traversal'in KENDISI (teslim icindeki KODUN KENDI mantiginda) KANITLANMIS VE 100% KESIN, sadece YUKARI-AKIS (upstream) bir ucuncu-taraf SISTEMIN davranisi BELIRSIZ.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** N/A
* **Kanıt kaynağı:** `N/A`
* **Kanıt alıntısı:**
  ```
  
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** N/A

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._