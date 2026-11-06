# Bug Bounty Pasif Keşif Raporu — example.com (TEST ÇALIŞTIRMASI)

**Tarih:** 2026-10-31
**Çalıştıran araç:** `scripts/bugbounty/scan.sh --target example.com --github urkmezakin41-gif/shared-agents`
**Analiz eden:** bug-bounty-auditor agent

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** Bu bir **fonksiyonel test çalıştırmasıdır**. `example.com`
  IANA tarafından belgeleme/test amaçlı ayrılmış bir domaindir
  (RFC 2606), gerçek bir bug bounty hedefi değildir. Gerçek bir hedef
  için bu alan boş bırakılamaz; kullanıcı kendi mülkiyeti, yazılı bug
  bounty programı adı/URL'si veya sözleşme referansı sağlamalıdır.
* **Amaç:** `scan.sh` → `bug-bounty-auditor` pipeline'ının uçtan uca
  çalıştığını ve ağ politikası bir host'u engellediğinde veri icat
  etmeden "BLOCKED" olarak işaretlediğini doğrulamak.
* **Ham veri kaynağı:** `scripts/bugbounty/out/example.com/raw/` (repoya
  commitlenmedi — `.gitignore`'da, üçüncü taraf verisi barındırabilir)

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Tahmini Önem Derecesi:** N/A (bulgu yok)
* **Zafiyet Sınıfı (CWE):** N/A

## 🔍 2. TEKNİK KANIT VE KOD ANALİZİ

| Adım | Sonuç | Not |
|---|---|---|
| crt.sh alt alan adı sorgusu | HTTP 200, 3 sertifika kaydı döndü | `example.com`, `*.example.com`, `www.example.com`, `m.example.com`, `dev.example.com`, `products.example.com`, `support.example.com` görünüyor — bunlar crt.sh'nin örnek/test verisi, gerçek canlı alt alan adları değil (domain zaten işlevsiz bir test alanı). |
| CNAME sorgusu (DoH) | HTTP 400 (DoH sağlayıcısının sorgu formatı hatası) | Takeover analizi için yeterli veri yok; **halüsinasyon yapılmadı**, boş bırakıldı. |
| Ana sayfa taraması | HTTP 200, 0 adet `.js` referansı bulundu | `example.com` statik, script içermeyen bir sayfa; endpoint/secret analizi için materyal yok. |
| GitHub son commit diff (`urkmezakin41-gif/shared-agents`) | HTTP 200, 1 commit (`8d96fdb`) incelendi | Eklenen dosya `auto_enter_bot.py`: yerel Windows klavye otomasyonu (Enter tuşu gönderen bir araç). IDOR/SSRF/hardcoded-secret/erişim-kontrolü sınıflarından **hiçbiri için somut kanıt yok**; bu script zaten bu repo kapsamındaki bilinen bir dosya, dışarıya açık bir servis/endpoint değil, dolayısıyla AppSec bounty sınıflarına girecek bir bulgu üretmiyor. |

**Sonuç:** Toplanan veride Zero-False-Positive eşiğini geçen (somut kanıtlı)
hiçbir bulgu yok. Ağ politikasının engellediği/kısıtladığı adımlar (DoH 400
yanıtı) veri icat edilmeden olduğu gibi raporlandı.

## 📝 3. HackerOne/Immunefi Taslağı
Üretilmedi — bu test çalıştırmasında `High`/`Critical` eşiğini geçen bir
bulgu yok.

## 📦 4. Pipeline Doğrulama Notu
* `scan.sh` ağ erişimi olan adımlarda (crt.sh, ana sayfa, GitHub API)
  gerçek veri çekti; önceki manuel testlerde bu ortamın egress
  politikası crt.sh/cloudflare-dns/örnek sitelere zaman zaman 403/timeout
  ile engel koydu — script bu durumda `BLOCKED_OR_UNREACHABLE` kaydı
  bırakıp devam ediyor, hiçbir adımda veri icat etmiyor. Ortamın ağ
  erişimi tutarsız olduğundan gerçek bir hedefte script'i çalıştırmadan
  önce ilgili host'ların o an erişilebilir olduğunu `_scan.log`'dan teyit
  edin.
* Gerçek bir hedef için bu script yalnızca **elle, açık bir `--scope`
  beyanıyla** çalıştırılır; otomatik/zamanlanmış tetikleme yoktur.
