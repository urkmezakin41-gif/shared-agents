# Bug Bounty Raporu — coinbase_coinbase-business-magento

**Tarih:** 2026-11-02 15:44 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/coinbase-business-magento - Adobe Commerce/Magento 2 USDC odeme gateway modulu).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_coinbase-business-magento/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; gercek bir Magento kurulumunda calistirilmadi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Bu modul, onceki turda coinbase-business-woocommerce/whmcs'de bulunan 'tutar/para birimi dogrulamasi olmadan odeme onaylama' sinifina karsi ACIKCA SERTLESTIRILMIS: Webhook.php'nin findPaymentMismatch() fonksiyonu, webhook imzasi gecerli olsa DAHI, odenen tutar+para birimini (settlement.totalAmount/currency) siparisin GERCEK baseGrandTotal'i ile (cent hassasiyetinde, float kaymasini onlemek icin int cent karsilastirmasi) CAPRAZ DOGRULUYOR; uyusmazlik varsa fatura KESMIYOR, siparisi 'hold' durumuna alip 'manuel inceleme' icin isaretliyor. Kod yorumunda bu tasarim kasti olarak aciklanmis ('A valid signature only proves Coinbase sent the event; it does not prove the customer paid what the order is worth').
* WebhookSignatureValidator.php: HMAC-SHA256 (Stripe-benzeri t=...,h=...,v1=... semasi), hash_equals() ile sabit-zamanli karsilastirma, 5 dakikalik zaman damgasi penceresi (replay koruması). RedirectHash.php: musteri-yonlendirme URL'sindeki order_id+hash parametresi icin ayni HMAC+hash_equals deseni - sahteciliğe karsi korunakli; ayrica ReturnAction.php zaten SIPARIS DURUMUNU DEGISTIRMIYOR (sadece okuyor), bu yuzden bu hash'in teorik olarak kirilmasi bile tek basina bir odeme-atlatma saglamiyor.
* CheckoutBuilder.php (odeme tutari) ve CheckoutDataBuilder.php (metadata.orderId): HER IKISI de AYNI sunucu-tarafi $order nesnesinden turetiliyor (kullanicidan gelen hicbir parametre yok) - 'ucuz bir siparis odeyip pahali bir siparisin metadata.orderId'sine yonlendirme' sinifi bir saldiri mumkun degil, cunku tutar ve orderId HER ZAMAN AYNI siparise bagli.
* CurrencyValidator.php / CheckoutBuilder.php: sadece USD taban para birimli magazalar icin odeme yontemini etkinlestiriyor (fail-closed), USDC 1:1 varsayimini yanlislikla baska bir para birimine uygulamayi onluyor.
* JwtGenerator.php (CDP API kimlik dogrulamasi icin ES256 JWT): nonce icin PHP'nin GUVENLI random_bytes(16) fonksiyonunu kullaniyor (cdp-sdk Python SDK'daki onceki turda bulunan guvensiz random.choices sorunuyla TEZAT olusturuyor - burada dogru yapilmis). Secrets (api_private_key, webhook_secret) Magento'nun EncryptorInterface'i ile sakli/cozuluyor (standart Magento guvenlik deseni).
* CleanupExpiredOrders.php (cron): bir siparisi iptal etmeden once Coinbase API'sinden GERCEK zAMAN durumunu kontrol ediyor (COMPLETED/PROCESSING ise iptal etmiyor) - webhook/cron arasi yaris durumuna karsi ek bir savunma katmani.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._