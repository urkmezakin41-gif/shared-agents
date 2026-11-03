# Bug Bounty Raporu — coinbase_fuzzy-trie

**Tarih:** 2026-11-03 03:39 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/coinbase/* -> https://github.com/coinbase/fuzzy-trie (structured_scope id: 1028888, eligible_for_bounty: true, max_severity: critical). Language: Go. Description: A trie-based solution to provide fuzzy searching.
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_fuzzy-trie/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Coinbase'in genel-amacli trie-tabanli bulanik (fuzzy) arama kutuphanesi (coinbase/fuzzy-trie). Kripto, kimlik dogrulama, agdan veri alma veya fon tasima mantigi icermiyor -- is mantigi (business logic) acisindan dusuk/orta onem derecesine sahip, ancak kapsam HackerOne structured_scope 1028888 (coinbase/* wildcard, max_severity: critical) altinda oldugundan tam inceleme yapildi.
* Son iki commit diff'i (a5ac47f54d, 6865fc1674) yalnizca go.mod/go.sum icindeki dolayli (indirect) test bagimliliklarinin (golang.org/x/net, x/sys, x/text) surum yukseltmelerini icerir -- guvenlik acisindan onemsiz, bilinen/resmi Go modul surumlerine yukseltme.
* pkg/levenshtein/levenshtein.go: standart O(min(m,n)) bellek kullanan Levenshtein mesafe algoritmasi, dogru uygulanmis, bellek/dizi tasma riski yok (Go bounds-checked slice erisimi, panic-ile-guvenli).
* pkg/trie/trie.go: Node.addItem() arama agacini yukleme zamaninda (LoadTree) kurar, rekursiyon derinligi terim uzunluguna bagli -- ancak bu, sabit/onceden-yuklenen veri kumesinden (items []T) calisir, saldirgan tarafindan calisma-zamaninda kontrol edilen bir girdi degil. Node.Contains() ve getLeafNodes() rekursiyonsuz/dongu-tabanli uygulanmis ('Don't use recursion just in case it's a very deep tree' yorumuyla acikca belirtilmis) -- derin agaclarda stack overflow riskine karsi bilincli onlem.
* pkg/trie/distance_tree.go (DistanceTrees.Search/searchTree/evaluate): arama terimi (searchTerm) parametresi calisma-zamaninda disaridan (potansiyel olarak kullanici girdisi) alinabilir ve her node icin LevenshteinDistance hesaplaniyor -- olasi bir algoritmik-karmasiklik (DoS) yuzeyi gibi gorunse de, searchTree() dongusu HER ITERASYONDA context.Cause(ctx) kontrolu yapiyor ve cagiran tarafin ctx'e timeout/cancellation ekleyebilmesini sagliyor; bu, kutuphanenin KASITLI ve zaten var olan DoS-sinirlama mekanizmasi (README'de de Timer/SetTimer araciligiyla performans olcumu destekleniyor). Herhangi bir bypass veya context kontrolunun atlandigi bir kod yolu bulunamadi.
* normalizeTerm() (strings.go) basit strings.ToUpper -- Unicode normalizasyon/homograph sorunlari bu kutuphanenin kapsaminda guvenlik-kritik bir etki yaratmiyor (yalnizca arama anahtari esitlemesi icin).
* SONUC: Teslim edilen veri (yalnizca trivial bagimlilik surumu diff'leri + tam kaynak kod statik incelemesi) icinde PASS veya hint-tier seviyesinde raporlanabilir bir guvenlik acigi TESPIT EDILEMEDI. Kutuphane, DoS'a karsi kasitli context-cancellation korumasi iceriyor ve bellek-guvenli/rekursiyonsuz veri yapilari kullaniyor. Temiz rapor (findings=[]) teslim ediliyor.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._