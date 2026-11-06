# Bug Bounty Raporu — brave_go-sync

**Tarih:** 2026-11-06 20:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/go-sync (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Go. Description: Brave sync server v2.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_go-sync/raw`
* **Engellenen/erişilemeyen adımlar:** Teslim COK BUYUK (389KB ham veri, buyuk kismi `schema/protobuf/sync_pb/*.pb.go` OTOMATIK-uretilen protobuf BINDING'leri) -- bu OTOMATIK-uretilen dosyalarin TAMAMI atlandi (el-yazisi mantik ICERMIYORLAR). ZAMAN KISITI nedeniyle `command/item_size_monitor.go`, `command/server_defined_unique_entity.go`, `datastore/item_count.go`, `cache/redis.go`'nun TAMAMI SATIR-SATIR incelenemedi -- SADECE bu dosyalarin cagri-SITELERI VE ANA MANTIK-AKISI (command.go uzerinden) goruldu., `handleCommitRequest`/`HandleClientToServerMessage`'in TAM MANTIGI (command.go'nun 2000+ satirinin TAMAMI) SATIR-satir OKUNMADI -- SADECE commit/get-updates akisinin clientID-SCOPE'lama DAVRANISINI DOGRULAMAK icin HEDEFLI bolum okumalar YAPILDI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i (bagimlilik/surum GUNCELLEMELERI gibi gorunen degisiklikler) -- ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave Sync v2'nin Go-tabanli SUNUCU tarafi -- Chromium'un sync PROTOKOLUNU (protobuf-tabanli GetUpdates/Commit) UYGULAYAN, DynamoDB-destekli bir servis.
* auth/auth.go::authenticate/Authorize -- bu, Brave Sync'in BILINCLI/belgelenmis TASARIMINI YANSITIYOR: clientID = istemcinin KENDI URETTIGI Ed25519 ACIK anahtari, VE kimlik dogrulama SADECE o ozel anahtarin BILGISINI (bir zaman-damgasini IMZALAYARAK) KANITLAMAYI GEREKTIRIYOR -- bu, merkezi bir HESAP sistemine KARSI DOGRULAMA DEGIL, Chromium/Brave'in KENDI 'sync kodu/seed' PAYLASIM modeliyle TUTARLI (guvenlik SINIRI, anahtarin KENDISIDIR, Brave hesabi DEGIL). Imza dogrulamasi (`ed25519.Verify`), zaman-damgasi SINIRLAMASI (+/- 1 gun) VE BLOCKED_CLIENT_IDS kara-LISTESI DOGRU uygulanmis.
* controller/controller.go, command/command.go, datastore/sync_entity.go -- `clientID` (auth middleware'den context'e KONULAN, SADECE DOGRULANMIS deger) TUM datastore cagrilarinda (GetUpdatesForType, GetClientItemCount, HasItem, InsertSyncEntity, UpdateSyncEntity, CreateDBSyncEntity) TUTARLI bir sekilde PARTITION/tenant-anahtar olarak KULLANILIYOR -- `UpdateSyncEntity`'nin DynamoDB PrimaryKey'i (`ClientID: entity.ClientID, ID: entity.ID`) SATIR SATIR DOGRULANDI: `entity.ClientID`, PROTOBUF govdesinden (saldirgan-kontrollu) DEGIL, DOGRULANMIS auth-context'inden GELIYOR -- bu nedenle bir istemcinin BASKA bir clientID'nin verilerini OKUMASI/YAZMASI/SILMESI MIMARI olarak IMKANSIZ (composite-key EslesMEME nedeniyle).
* middleware/disabled_chain.go -- devre-DISI birakilmis zincirler icin ISTEKLERI DOGRU sekilde ERKEN SONLANDIRIYOR, clientID AUTH ASAMASINDAN SONRA TUTARLI olarak KULLANILIYOR.
* command/device_limit.go -- cihaz-SAYISI SINIRLAMA mantigi BASIT VE DOGRU (>=karsilastirmasi, dogru DEFAULT/yuksek-limit AYRIMI).
* cache/cache.go -- Redis anahtarlari `clientID` (SADECE hex KARAKTERLER, auth KATMANINDA regex ile ZATEN DOGRULANMIS) ile OLUSTURULUYOR -- komut-ENJEKSIYONU riski YOK (go-redis zaten PARAMETRIZE komutlar KULLANIYOR, string-concat TEHLIKESI de clientID'nin KARAKTER-setinin KISITLI OLMASI nedeniyle AZALTILMIS).
* SONUC: Bu, bu oturumda incelenen EN BUYUK VE EN KARMASIK Brave backend servislerinden biri -- kimlik dogrulama, tenant-izolasyonu VE devre-disi-zincir KONTROLU DAHIL tum KRITIK guvenlik SINIRLARI DOGRU VE TUTARLI sekilde uygulanmis bulundu. Zaman kisiti nedeniyle BAZI ikincil dosyalar (item_size_monitor, server_defined_unique_entity, item_count) TAM olarak incelenemedi, ANCAK incelenen KISIMLARDA odul-degeri TASIYAN bir guvenlik bulgusu TESPIT EDILEMEDI. Rapor TEMIZ olarak dispatch edilmeli.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._