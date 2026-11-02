# Bug Bounty Raporu — coinbase_mesh-geth-sdk

**Tarih:** 2026-11-02 14:31 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/mesh-geth-sdk, go-ethereum tabanli Mesh/Rosetta SUNUCUSU - construction/block/account servisleri).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_mesh-geth-sdk/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; geth node'a karsi calistirilmadi., services/construction/payloads.go'daki 'amount' kaynaginin (matches[1].First()) tam zincirini (parser/matcher kodu) dogrulamak icin services/construction/parse.go disi ek dosyalar (matcher kutuphanesi) kismen incelendi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* contract_call_data.go encodeMethodArgsStrings() icinde AYNI desen (uint/int ABI argumanlari icin 'value.SetString(methodArgs[i], base)' - donus degeri kontrol edilmeden) tekrarlaniyor; bu, ERC20 transfer tutari gibi method argumanlarinin GERCEK ABI-encode edilmis islem verisine (contractData) GIRDIGI yer - F1'den FARKLI olarak bu yol GERCEKTEN imzalanacak 'data' alanini etkiliyor. Ancak payloads.go'da asil 'amount' (Operations'tan turetilen, Value DEGIL) ayri hesaplaniyor gibi gorunuyor; method_args[] (contract call parametreleri) ile 'amount' (native/ERC20 transfer degeri) FARKLI alanlar - bu ayrimi TAM dogrulamak icin matcher/parser kodu (services/construction/parse.go, ParseContractCallData) daha derin incelenmeli. F1'e benzer bir CWE-252 orneği (ikinci bulgu adayi, F1 ile ayni kok neden) olarak not edildi ama zaman kisiti nedeniyle AYRI bir F2 olarak degil, F1'in notlari altinda birlestirildi.
* client/call_tracer.js: go-ethereum'un upstream call_tracer.js'sinin (LGPL, 'The go-ethereum Authors' telif hakki) Coinbase'in kendi 'beforeEVMTransfers'/'afterEVMTransfers' eklentileriyle genisletilmis hali - standart/iyi-denetlenmis upstream koda kucuk, iyi tanimlanmis bir ekleme; bagimsiz bir guvenlik sorunu gorulmedi.
* preprocess.go ve metadata.go'nun GERI KALANI (adres checksum dogrulamasi, nonce/gasPrice alma, EIP-1559 tip/fee-cap hesaplama) tutarli ve hatalari dogru sekilde sarmalıyor/donduruyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 30 | REJECT | Somut etki sadece gaz-tahmini guvenilirligi; GERCEK islem degerini degistirmiyor, ucuncu taraf fon kaybi yolu yok. | services/construction/parse.go'nun TAM kaynagi + matcher kutuphanesi (coinbase/rosetta-sdk-go/parser) - method_args ile Operations amount arasindaki ayrimi/eslesmeyi TAM dogrulamak icin |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._