# Bug Bounty Raporu — coinbase_coinbase-business-whmcs

**Tarih:** 2026-11-02 16:51 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/coinbase-business-whmcs, WHMCS Coinbase Business USDC odeme modulu). Bu hedef onceki turda da incelenmisti (WooCommerce+WHMCS+Magento paketinin bir parcasi olarak); bu turda modul TEK BASINA, kardes Magento modulunun hash-korumali esdegeriyle KARSILASTIRMALI olarak yeniden degerlendirildi.
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_coinbase-business-whmcs/raw`
* **Engellenen/erişilemeyen adımlar:** Gercek bir WHMCS kurulumunda (addInvoicePayment/suspension cron/reminder cron davranisi) calistirilip test edilmedi; WHMCS core'un 'Payment Pending' durumunu hangi cron'larda nasil ele aldigi WHMCS'in kendi (bu depoda olmayan) kaynagina dayaniyor - bu, genel bilgiye ve kod yorumlarindaki aciklamaya (satir: 'Sets invoice status to Payment Pending so the user sees confirmation instead of Unpaid while the async webhook is still in transit') dayanarak cikarilmistir.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* handlePaymentSuccess() (callback/coinbase.php) webhook'tan gelen settlement tutarini faturanin GERCEK tutariyla CAPRAZ DOGRULAMIYOR (Magento'nun findPaymentMismatch()'inin karsiligi yok) - ANCAK bu kendi basina YENI bir acik degil: redirect.php'de amount=$invoice->total VE metadata.invoiceid=$invoiceId AYNI sunucu-tarafi $invoice kaydindan geliyor (kullanicidan gelen bagimsiz bir parametre yok), yani 'ucuz fatura ode, pahali faturaya yonlendir' sinifi saldiri burada da mumkun degil. Asil fark tutari (WHMCS'in kendi addInvoicePayment() mantiginin kismi odemeleri dogru islemesine guveniliyor, Magento gibi ekstra bir app-seviyesi kontrol YOK) - bu tek basina raporlanabilir bir ek acik olusturmuyor, F1'in notlarina eklendi.
* CheckoutClient.php/JwtAuth.php: ES256 JWT uretimi dogru (random_bytes CSPRNG, private key loglanmiyor), HTTP istemci guvenli (sabit base_uri, timeout var).
* callback/coinbase.php webhook imza dogrulamasi (HMAC-SHA256, hash_equals, 5 dakika zaman penceresi) DOGRU uygulanmis - F1'in kapsami SADECE return.php (webhook degil).

## 📊 Bulgu F1: modules/gateways/coinbase/return.php: odeme kaniti olmadan (yalnizca GET invoice_id + oturum sahiplik kontrolu ile) fatura 'Unpaid' -> 'Payment Pending'e cevrilebiliyor; kardes Magento modulu AYNI adimi HMAC ile koruyor, bu modul korumuyor
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** Medium
* **Zafiyet Sınıfı (CWE):** CWE-840 (Business Logic Errors) / CWE-306 (Missing Authentication for Critical Function)
* **Stage 2 Confidence:** 75/100 — Kod-okuma ile tam dogrulandi: return.php hicbir kriptografik kanit istemeden durum degistiriyor; kardes Magento modulunde AYNI adim icin HMAC var, burada yok - bu net bir eksik kontrol. Etki (hatirlatma/askiya-alma atlatma) WHMCS'in belgelenen 'Payment Pending' semantigine dayanarak makul; dogrudan fon hirsizligi degil ama is-mantigi/erisim-kontrolu acigi olarak odul-degeri tasiyor.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** modules/gateways/coinbase/return.php (tum dosya); karsilastirma: modules/gateways/coinbase/redirect.php (successUrl olusturma, token eklenmiyor); kardes depo coinbase-business-magento: Service/RedirectHash.php + Controller/Payment/ReturnAction.php (AYNI amac icin HMAC kullaniyor)
* **Kanıt kaynağı:** `scripts/bugbounty/out/coinbase_coinbase-business-whmcs/raw/ingested_incoming_2026-11-02T18-46-25_coinbase_coinbase-business-whmcs.json`
* **Kanıt alıntısı:**
  ```
  // redirect.php: $successUrl = $systemUrl . 'modules/gateways/coinbase/return.php?invoice_id=' . $invoiceId;  [TOKEN YOK]\n// return.php: if ($loggedInUserId !== (int) $invoice->userid) { die('Unauthorized access to invoice'); }\nCapsule::table('tblinvoices')->where('id', $invoiceId)->where('status', 'Unpaid')->update(['status' => 'Payment Pending']);
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** return.php, Coinbase'in GERCEKTEN bu URL'ye yonlendirdigine dair HICBIR kriptografik kanit (hash/token/nonce) istemiyor - sadece GET invoice_id ve oturumdaki kullanicinin o faturanin sahibi olmasi yeterli. Giris yapmis HERHANGI bir musteri, kendi odenmemis herhangi bir faturasi icin HICBIR odeme yapmadan, HICBIR Coinbase checkout oturumu olusturmadan, dogrudan bu URL'yi ziyaret ederek faturayi 'Payment Pending'e cevirebilir. revertPaymentPending() SADECE webhook'un checkout.payment.failed/expired olaylariyla cagriliyor - bu olaylar da yalniz GERCEKTEN olusturulmus bir checkout oturumu icin tetiklenir. Checkout hic olusturulmadiysa (kullanici return.php'yi dogrudan ziyaret ettiyse), faturayi 'Unpaid'e GERI DONDURECEK HICBIR OTOMATIK mekanizma YOK - durum SONSUZA KADAR 'Payment Pending' kalir (yalniz bir admin elle degistirirse degisir). Kardes Magento modulu AYNI adimi (musteri-yonlendirme sonrasi durum okuma - orada durum DEGISTIRILMIYOR, sadece okunuyor) orderId+storeId'ye baglanmis bir HMAC (RedirectHash) ile koruyor; bu modul AYNI korumayi HIC uygulamiyor VE (Magento'dan farkli olarak) bu adimda GERCEKTEN DURUM DEGISTIRIYOR.
* **Nasıl Doğrulanır (Güvenli Doğrulama Adımları):**
  1. Bir WHMCS test kurulumunda, Coinbase Business gateway'i aktif bir musteri hesabiyla odenmemis bir fatura olustur.
  2. 'Pay Now' butonuna TIKLAMADAN (checkout olusturmadan), dogrudan tarayicida https://<whmcs>/modules/gateways/coinbase/return.php?invoice_id=<ID> adresini ac (musteri olarak giris yapmis halde).
  3. Admin panelinde faturanin durumunun 'Payment Pending'e dondugunu, hicbir odeme/checkout kaydi olmadigini dogrula.
  4. WHMCS'in hatirlatma/askiya-alma cron'larinin bu faturayi 'Payment Pending' oldugu icin atlayip atlamadigini (WHMCS core davranisi, genellikle 'Overdue'/'Unpaid' hedefler) kontrol et.

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
## Summary
`modules/gateways/coinbase/return.php` in the Coinbase Business WHMCS gateway marks an invoice "Payment Pending" with no cryptographic proof that any Coinbase checkout was ever completed - only a GET `invoice_id` parameter and a session-ownership check. Any logged-in WHMCS client can flip any of their own unpaid invoices to "Payment Pending" by visiting this one URL directly, without ever creating a Coinbase checkout or sending a payment.

## Root cause
`redirect.php` builds the Coinbase `successRedirectUrl` as:
```php
$successUrl = $systemUrl . 'modules/gateways/coinbase/return.php?invoice_id=' . $invoiceId;
```
No token, nonce or HMAC is appended. `return.php` then does only:
```php
$loggedInUserId = isset($_SESSION['uid']) ? (int) $_SESSION['uid'] : 0;
if ($loggedInUserId !== (int) $invoice->userid) { die('Unauthorized access to invoice'); }
Capsule::table('tblinvoices')->where('id', $invoiceId)->where('status', 'Unpaid')->update(['status' => 'Payment Pending']);
```
There is no verification that Coinbase ever redirected the browser here, no signature, and no linkage to an actual checkout session.

By contrast, the sibling Magento module (`coinbase-business-magento`) protects the exact same return-redirect step with an HMAC bound to `orderId|storeId` (`RedirectHash::generate()`/`isValid()`, using the webhook secret), which an attacker cannot forge. The WHMCS module omits this control entirely for the same code path.

## Impact
Because "Payment Pending" is a non-final state, and `revertPaymentPending()` is only ever called from the webhook callback on `checkout.payment.failed` / `checkout.payment.expired` - events that only fire for a Coinbase checkout session that was actually created - an invoice flipped to "Payment Pending" by directly visiting `return.php` (with no checkout ever created) has **no automatic path back to "Unpaid"**. A customer can use this to indefinitely:
- suppress WHMCS's unpaid-invoice reminder emails, and
- avoid WHMCS's automatic suspension-for-non-payment logic (which typically targets "Overdue"/"Unpaid" invoices, not "Payment Pending" ones),

for any invoice on their own account, without ever paying, by making one unauthenticated-to-Coinbase GET request.

## Steps to reproduce
1. Log in to a WHMCS client account with an unpaid invoice using the Coinbase Business gateway, invoice id `<ID>`.
2. Do **not** click "Pay Now" (do not create a Coinbase checkout).
3. Navigate directly to `https://<whmcs-host>/modules/gateways/coinbase/return.php?invoice_id=<ID>`.
4. Observe the invoice status in the admin area or client portal is now "Payment Pending" even though no payment was made and no Coinbase checkout session exists.
5. Observe no further webhook will ever arrive to revert this (no checkout was created to fail/expire), so the invoice remains in this state indefinitely unless an admin manually reverts it.

## Suggested fix
Mirror the Magento module's `RedirectHash`: generate an HMAC (bound to invoice id + a short random nonce, using the webhook secret) at checkout-creation time, append it to `successUrl`/`failUrl`, and require `return.php` to verify it (`hash_equals`) before changing invoice status - failing closed exactly as the Magento module already does.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._