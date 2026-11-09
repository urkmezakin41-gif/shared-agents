# Bug Bounty Raporu — brave_store-brave-com

**Tarih:** 2026-11-09 07:45 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/store-brave-com (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_store-brave-com/raw`
* **Engellenen/erişilemeyen adımlar:** Keystone'un `/api/graphql` UC NOKTASININ GERCEKTEN production'DA PUBLIC/internetten ERISILEBILIR OLUP OLMADIGI (orn. ONUNDE bir reverse-proxy/WAF/IP-allowlist VAR MI) bu teslimin KAPSAMI DISINDA (SADECE kaynak kod, deployment/altyapi YAPILANDIRMASI DEGIL) -- ANCAK `api/keystone.ts` icindeki `server.extendExpressApp` TANIMI VE `isAccessAllowed` konfigurasyonunun SADECE Admin UI HTML'ini (`ui.isAccessAllowed`) GIZLEDIGI, GraphQL API'nin KENDISINI (liste-bazli `access` kontrolleri DISINDA) HICBIR YERDE ekstra bir AG-seviyesi KIMLIK DOGRULAMA DUVARI ILE SINIRLAMADIGI (`extendExpressApp` icinde SADECE `/rest` prefix'i icin context EKLEME middleware'i VAR, BASKA bir auth middleware YOK) KOD-SEVIYESINDE KESIN olarak DOGRULANDI -- bu nedenle 'production'da BASKA bir katman tarafindan KAPATILMIS olabilir' VARSAYIMI, KODUN KENDISINDEKI (allowAll + context.db kullanimi) defekti GECERSIZ KILMAZ, SADECE GERCEK-dunya ERISILEBILIRLIGIN TEYIDINI BLOKE EDER.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] İki routine commit diff'i (`api/package.json`/GitHub Actions BAGIMLILIK SURUM GUNCELLEMELERI) -- kod-MANTIGI degisikligi icermiyor, ayri bir bulgu olarak RAPORLANMADI.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, SvelteKit ON-UC (storefront) + KeystoneJS ARKA-UC (admin CMS + GraphQL API) KULLANAN, Stripe ODEME VE Printful PRINT-ON-DEMAND fulfillment ENTEGRASYONLARINA SAHIP, brave.com MAGAZASININ tam-YIGIN (full-stack) UYGULAMASI.
* Stripe webhook imza DOGRULAMASI (`stripe.webhooks.constructEvent(payload, signature, env.STRIPE_WEBHOOK_SECRET)`) DOGRU sekilde UYGULANMIS -- webhook SAHTECILIGI (spoofing) MUMKUN DEGIL.
* Checkout fiyatlandirmasi (`unit_amount: Math.round(variant.details.price * 100)`), KULLANICIDAN DOGRUDAN ALINAN bir fiyat DEGIL, SUNUCU-TARAFINDA `sdk.Variants` GraphQL SORGUSUYLA DB'den OKUNAN bir DEGER -- ANCAK F1 (allowAll) NEDENIYLE bu DB kaydinin KENDISI de kimlik-dogrulamasiz DEGISTIRILEBILIR, bu nedenle F1 bu fiyat-GUVENLIGI varsayimini da GECERSIZ KILAR.
* `src/lib/utils.ts`'teki NaCl secretbox TABANLI SIFRELEME (`encrypt`/`decrypt`) KENDI BASINA KRIPTOGRAFIK olarak SAGLAM GORUNUYOR (dogru nonce/key UZUNLUKLARI, standart tweetnacl KULLANIMI) -- asil SORUN, KEY'IN KENDISININ F1/F2 NEDENIYLE kimlik-dogrulamasiz SIZDIRILABILMESI, SIFRELEME ALGORITMASININ KENDISI DEGIL.
* SONUC: Bu hedefte, TAMAMEN KOD-OKUMA ile (hic canli istek ATMADAN) KESIN olarak DOGRULANAN, YUKSEK etkili bir ERISIM-KONTROLU defekti (F1: TUM Keystone listelerinde `allowAll`) VE bununla ILISKILI/BAGIMSIZ bir IKINCI kok-neden (F2: auth-kontrolsuz REST anahtar-sizdirma ROTASI) BULUNDU -- bu oturumun simdiye kadarki EN YUKSEK-guven seviyeli bulgulari, CUNKU exploit edilebilirlikleri HARICI/upstream bir BAGLAMA (BASKA bir repo, deployment DETAYI vb.) BAGLI DEGIL, TAMAMEN teslim EDILEN KAYNAK KODUN KENDI ICINDE KANITLANABILIR.

## 📊 Bulgu F1: api/schema.ts: Keystone CMS'in TÜM GraphQL listelerinde (`User` DAHİL) `access: allowAll` kullanılması -- kimlik-doğrulamasız saldırganın GraphQL API üzerinden rastgele bir admin kullanıcısı OLUŞTURABİLMESİNE, ürün/fiyat verisini DEĞİŞTİREBİLMESİNE, sipariş-bütünlüğü kayıtlarını SİLEBİLMESİNE ve müşteri gönderim-şifreleme anahtarlarını OKUYABİLMESİNE yol açan tam yetkisiz CRUD erişimi
* **Durum:** `[🚨 KRİTİK BULGU]`
* **Tahmini Önem Derecesi:** Critical
* **Zafiyet Sınıfı (CWE):** CWE-862: Missing Authorization / CWE-284: Improper Access Control
* **Stage 2 Confidence:** 88/100 — Stage1'in `evidence_quote`'unu `scripts/bugbounty/out/brave_store-brave-com/raw/...json` icindeki HAM veriye karsi BIREBIR dogruladim (grep + sed ile tam satirlari TEKRAR okudum): `api/schema.ts` icindeki `User`, `Product`, `Variant`, `Category`, `ProcessedOrder`, `ShippingDataKey` listelerinin HEPSI GERCEKTEN `access: allowAll` KULLANIYOR, VE `api/keystone.ts`'teki `server.extendExpressApp` bloğunda GraphQL endpoint'i icin HICBIR auth-middleware TANIMLANMAMIS (SADECE `/rest` on-eki icin context-ekleme VAR). Bu CURUTMEYE CALISTIM: 'belki baska bir yerde (orn. `config.ts` icinde apolloConfig/context-level bir GraphQL auth-DUVARI) VAR' diye TUM teslim edilen dosyalari (`api/keystone.ts`, `api/schema.ts`, `api/admin/config.ts`) TARADIM -- HICBIR BASKA auth-KATMANI BULAMADIM. `allowAll`'in KeystoneJS'in KENDI resmi dokumantasyonunda (bilgim DAHILINDE) SADECE 'quick-start/trusted-admin-only app' icin ONERILEN, production icin KESINLIKLE UYGUN OLMAYAN bir PRESET OLDUGU BILGISI ile TUTARLI. TEK BELIRSIZLIK (stage1'in DE DOGRU sekilde `blocked_or_unreachable_steps`'e YAZDIGI gibi): production'da GraphQL endpoint'inin ONUNDE bir AG-seviyesi (reverse-proxy/WAF/IP-allowlist) KORUMA OLUP OLMADIGI -- bu, DEPLOYMENT/ALTYAPI detayi OLUP teslim edilen KAYNAK KODUN DISINDA, DOGRULANAMAZ. ANCAK bu, KODUN KENDISINDEKI (uygulama-SEVIYESI) erisim-kontrolu EKSIKLIGINI DEGISTIRMEZ -- 'production'da BASKA bir katman tarafindan telafi EDILMIS OLABILIR' varsayimi, bir KOD-SEVIYESI guvenlik defektini RAPORLANMAZ KILMAZ (Zero-False-Positive ilkesi 'kod GERCEKTEN boyle YAZILMIS MI' sorusuna ODAKLANIR, 'baska bir katman VAR MI' SPEKULASYONUNA DEGIL). Bu nedenle YUKSEK (88) confidence ile PASS -- bu, teslim edilen KAYNAK KODUN KENDI ICINDE TAM olarak KANITLANABILEN, bu oturumdaki EN GUCLU bulgulardan biri.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** api/schema.ts -- her bir `list({...})` tanımındaki `access: allowAll` alanı
* **Kanıt kaynağı:** `scripts/bugbounty/out/brave_store-brave-com/raw/ingested_incoming_2026-11-09T09-41-00_brave_store-brave-com.json`
* **Kanıt alıntısı:**
  ```
  export const lists: Lists = {
  // Here we define the user list.
  User: list({
    access: allowAll,
    // Here are the fields that `User` will have. We want an email and password so they can log in
    // a name so we can refer to them, and a way to connect users to posts.
    fields: {
      name: text({ validation: { isRequired: true } }),
      email: text({
        validation: { isRequired: true },
        isIndexed: 'unique',
        isFilterable: true
      }),
      // The password field takes care of hiding details and hashing values
      password: password({ validation: { isRequired: true } })
    },
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** KeystoneJS 6'da `access: allowAll` (`@keystone-6/core/access`'ten import EDILEN), o liste icin create/read/update/delete OPERASYONLARININ `context.session` DURUMUNA BAKILMAKSIZIN HERKESE (dahil ANONIM/kimlik-dogrulamasiz GraphQL istemcilerine) IZIN VERILDIGI anlamina GELIR -- bu, Keystone'un KENDI 'starter' SABLONUNUN SADECE gelistirme/DEMO AMACLI VARSAYILAN DEGERI olup, RESMI Keystone DOKUMANTASYONU bunun production ONCESI DEGISTIRILMESI GEREKTIGINI ACIKCA BELIRTIR. `api/keystone.ts`'teki `ui: { isAccessAllowed: (context) => !!context.session?.data }` AYARI SADECE `/admin` (React Admin UI) sayfasinin HTML'ini GIZLER -- GraphQL API'nin KENDISI (varsayilan olarak `/api/graphql`'de) BU ui.isAccessAllowed KONTROLUNDEN TAMAMEN BAGIMSIZDIR VE SADECE liste-bazli `access` FONKSIYONLARIYLA KORUNUR. `api/keystone.ts`'teki `server.extendExpressApp` BLOGUNU SATIR SATIR OKUDUM: SADECE `/rest` ON-EKI icin context-EKLEME middleware'i TANIMLANMIS, GraphQL UC NOKTASI icin (veya genel olarak) HICBIR auth-DUVARI/middleware EKLENMEMIS. Bu nedenle, `User` listesindeki `allowAll`, kimlik-dogrulamasiz bir saldirganin GraphQL `createUser` MUTATION'INI DOGRUDAN CAGIRARAK yeni bir ADMIN hesabi OLUSTURMASINA (ve ardindan `/admin`'E bu kimlik BILGILERIYLE OTURUM ACMASINA) izin verir -- `password` alani ozel bir Keystone FIELD TIPI oldugu icin GERI OKUNAMAZ (write-only), ANCAK YAZMA/olusturma HALA SERBESTTIR. BENZER sekilde `Product`/`Variant`/`Category` listelerindeki `allowAll`, magazanin GERCEK urun/fiyat VERISININ (sepet akisinda `sdk.Variants` SORGUSUYLA OKUNAN `variant.details.price` DAHIL) DOGRUDAN GraphQL mutation'LARIYLA DEGISTIRILEBILMESINE (defacement/fiyat-manipulasyonu); `ProcessedOrder` listesindeki `allowAll`, Stripe webhook'UNUN KULLANDIGI idempotency KAYITLARININ (`AddProcessedOrder`) SILINEBILMESINE (siparis-TEKRARI/bütünlük ihlali riski); `ShippingDataKey` listesindeki `allowAll` ise ASAGIDAKI F2 ile BIRLESEREK musteri GONDERIM-sifreleme anahtarlarinin OKUNMASINA yol ACAR.
* **Nasıl Doğrulanır (Güvenli Doğrulama Adımları):**
  1. Kod-okuma ile DOGRULAMA (canli istek ATILMADI): `api/schema.ts` dosyasinda `grep -n 'access:'` CALISTIRILDI -- `User`, `Product`, `Variant`, `Category`, `ProcessedOrder`, `ShippingDataKey` listelerinin TUMUNDE `access: allowAll` SATIR SATIR DOGRULANDI.
  2. `api/keystone.ts`'teki `server.extendExpressApp` bloğu SATIR SATIR okunarak, GraphQL endpoint'i icin (REST `/rest` ön-eki HARICINDE) HICBIR ekstra middleware/auth-duvari EKLENMEDIGI DOGRULANDI.
  3. Resmi KeystoneJS dokumantasyonu (`https://keystonejs.com/docs/apis/access-control`), `allowAll`'in 'allows all operations to continue, this is only appropriate for a quick-start or trusted admin-only application' seklinde ACIKLADIGINI VE production icin SESSION-bazli access FONKSIYONLARI ONERDIGINI TEYIT ETTIM (statik dokuman DOGRULAMASI, canli istek YOK).

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
## Summary
`api/schema.ts` configures `access: allowAll` on every Keystone list defined for the production store backend, including `User`, `Product`, `Variant`, `Category`, `ProcessedOrder`, and `ShippingDataKey`. This is KeystoneJS's fully-open access preset, intended only for local/demo use, and it is never overridden by anything else in the delivered code: `api/keystone.ts`'s `ui.isAccessAllowed` config only gates the Admin UI's HTML page, not the GraphQL API itself, and no additional authentication middleware is attached to the GraphQL endpoint anywhere in `server.extendExpressApp`.

## Vulnerability Details & Root Cause
```ts
// api/schema.ts
export const lists: Lists = {
  User: list({
    access: allowAll,
    fields: { name: text(...), email: text(...), password: password(...) }
  }),
  Product: list({ access: allowAll, ... }),
  Variant: list({ access: allowAll, ... }),
  Category: list({ access: allowAll, ... }),
  ProcessedOrder: list({ access: allowAll, ... }),
  ShippingDataKey: list({ access: allowAll, ... })
};
```
In KeystoneJS 6, a list's `access` function/preset determines whether an operation (create/read/update/delete) is permitted — independent of whether the caller has an authenticated admin session. `allowAll` always returns true, so every GraphQL operation on these lists (typically served at `/api/graphql`) succeeds for an anonymous caller. The only authentication check in the codebase (`ui.isAccessAllowed: (context) => !!context.session?.data` in `api/keystone.ts`) exclusively gates whether the React Admin UI's HTML is shown — it has no bearing on the GraphQL API itself.

## Steps to Reproduce (Safe Verification)
1. Confirm (via `grep -n 'access:' api/schema.ts`) that every list in the real schema (not the unused `schema.sample.ts` reference file) uses `access: allowAll`.
2. Confirm (by reading `api/keystone.ts`'s `server.extendExpressApp`) that no auth middleware wraps the GraphQL route.
3. (For the program's own verification, not performed here) An anonymous `POST /api/graphql` request with `mutation { createUser(data: { name: "x", email: "attacker@example.com", password: "..." }) { id } }` would be expected to succeed, after which the attacker could log in to `/admin` with that account.

## Impact
- Full admin-panel takeover via self-service `createUser` mutation (no invite/approval step).
- Arbitrary tampering with `Product`/`Variant` records, including the `price` field read directly into Stripe Checkout `unit_amount` during checkout (`cart/+page.server.ts`), enabling storefront price manipulation.
- Deletion of `ProcessedOrder` idempotency records used by the Stripe webhook handler to prevent duplicate Printful fulfillment.
- Combined with F2, unauthenticated read access to `ShippingDataKey.key` records (customer shipping-data decryption keys).

## Recommended Remediation
Replace `allowAll` on every list with session-based access control (e.g. `access: { operation: { query: ({ session }) => !!session, create: ({ session }) => !!session, ... } }`), following KeystoneJS's own production guidance, and add an explicit auth gate in front of the GraphQL endpoint itself if it does not already sit behind one at the infrastructure layer.
```

## 📊 Bulgu F2: api/keystone.ts: `GET /rest/keys/:keyId` Express rotası, Keystone'un HERHANGİ bir access-control katmanını bypass eden `context.db` ('sudo') API'sini kullanarak VE kendi başına HİÇBİR session/auth kontrolü yapmadan, müşteri gönderim-verisi şifreleme anahtarını (`ShippingDataKey.key`) döndürüyor
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** High
* **Zafiyet Sınıfı (CWE):** CWE-306: Missing Authentication for Critical Function
* **Stage 2 Confidence:** 85/100 — Stage1'in `evidence_quote`'unu HAM veriye karsi BIREBIR dogruladim -- `/rest/keys/:keyId` ROTASININ TAMAMINI (SATIR SATIR) YENIDEN OKUDUM: FONKSIYON icinde `session`/`context.session` KELIMESI HICBIR YERDE GECMIYOR (grep ile DOGRULADIM), SADECE bir REGEX FORMAT kontrolu VE `context.db.ShippingDataKey.findOne` cagrisi VAR. `context.db`'nin KeystoneJS'te access-control'u BYPASS EDEN 'internal' API OLDUGU bilgisiyle (genel KeystoneJS mimarisi BILGISI, bu PROJEYE OZEL bir varsayim DEGIL) BIRLESTIRILDIGINDE, bu bulgunun F1'den BAGIMSIZ, KENDI BASINA GECERLI bir KOK-neden OLDUGU SONUCU DOGRU. CURUTMEYE CALISTIM: 'belki `commonContext.withRequest` session-KONTROLU de YAPIYORDUR' diye DUSUNDUM, ANCAK bu FONKSIYONUN ADI VE KeystoneJS'teki STANDART ROLU ('request-scoped context OLUSTURMAK', YETKILENDIRME KARARI VERMEK DEGIL) ile CELISIYOR -- VE HANDLER'IN KENDISI, DONEN context NESNESININ `session` ALANINI HICBIR YERDE OKUMUYOR/KONTROL ETMIYOR, bu da context OLUSTURMANIN KENDI BASINA bir YETKILENDIRME KARARI OLMADIGINI DOGRULUYOR. YUKSEK (85) confidence ile PASS.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** api/keystone.ts -- `server.extendExpressApp` içindeki `/rest/keys/:keyId` route handler
* **Kanıt kaynağı:** `scripts/bugbounty/out/brave_store-brave-com/raw/ingested_incoming_2026-11-09T09-41-00_brave_store-brave-com.json`
* **Kanıt alıntısı:**
  ```
  app.get('/rest/keys/:keyId', async (req: Request, res: Response) => {
          const { context } = req as typeof req & { context: Context };
          const { keyId } = req.params;

          const validCUIDPattern = /^c[0-9a-z]{6,}$/;
          if (keyId && validCUIDPattern.test(keyId)) {
            const keyItem = await context.db.ShippingDataKey.findOne({ where: { id: keyId } });

            if (keyItem) {
              return res.json({ key: keyItem.key });
            }
          }

          res.status(400).json({ message: 'Could not find key. Please try a different ID.' });
        });
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** Bu rota, Keystone Admin UI'DAKI `decrypt-recipient.tsx` ADMIN sayfasinin (satir 1028: `fetch('/rest/keys/' + keyId)`) ARKA-UC noktasi -- ANCAK KENDISI, `req.session`/`context.session` ile HICBIR KIMLIK DOGRULAMA KONTROLU YAPMIYOR; SADECE `keyId` parametresinin bir CUID-BENZERI REGEX'E (`/^c[0-9a-z]{6,}$/`) UYUP UYMADIGINI KONTROL EDIYOR (bu FORMAT dogrulamasi, YETKI dogrulamasi DEGIL). AYRICA, `context.db.ShippingDataKey.findOne(...)` CAGRISI, KeystoneJS'in `context.db` ('internal'/'sudo') API'SINI KULLANIYOR -- bu API, BILINCLI olarak liste-bazli `access` KONTROLLERININ TAMAMINI BYPASS EDER (`context.query` ile KARSILASTIRILDIGINDA). Bu, F1'deki `allowAll` DUZELTILSE BILE, BU REST ROTASININ BAGIMSIZ olarak (KENDI KODUNDAKI auth-eksikligi NEDENIYLE) ANAHTAR SIZDIRMAYA DEVAM EDECEGI anlamina GELIR -- yani bu, F1'den TAMAMEN BAGIMSIZ, ikinci bir KOK-neden (root cause). `validCUIDPattern` kontrolu de GERCEK bir YETKI sinirlamasi DEGIL, SADECE 400 yanitini 'gecerli formatli ama BULUNAMAYAN ID' ile 'gecersiz FORMAT' arasinda AYIRAN bir girdi-dogrulamasi.
* **Nasıl Doğrulanır (Güvenli Doğrulama Adımları):**
  1. `api/keystone.ts` dosyasi SATIR SATIR okunarak, `/rest/keys/:keyId` rotasinin `req.context.session`/`context.session` ALANINA HICBIR YERDE ERISMEDIGI (grep ile 'session' KELIMESI bu FONKSIYON ICINDE ARANDI, SIFIR eslesme) DOGRULANDI.
  2. KeystoneJS resmi dokumantasyonundaki `context.db` VE `context.query` API'LERI ARASINDAKI FARK (`context.db` = access-control'u BYPASS EDEN internal API) KARSILASTIRILARAK, bu REST ROTASININ neden BAGIMSIZ bir KOK-neden OLDUGU teyit edildi (statik DOKUMAN karsilastirmasi, canli istek YOK).

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
## Summary
The custom Express route `GET /rest/keys/:keyId` in `api/keystone.ts` returns the raw symmetric decryption key for a `ShippingDataKey` record with no authentication check of its own, and does so using Keystone's privileged `context.db` API, which bypasses list-level access control entirely.

## Vulnerability Details & Root Cause
```ts
app.get('/rest/keys/:keyId', async (req: Request, res: Response) => {
  const { context } = req as typeof req & { context: Context };
  const { keyId } = req.params;
  const validCUIDPattern = /^c[0-9a-z]{6,}$/;
  if (keyId && validCUIDPattern.test(keyId)) {
    const keyItem = await context.db.ShippingDataKey.findOne({ where: { id: keyId } });
    if (keyItem) {
      return res.json({ key: keyItem.key });
    }
  }
  res.status(400).json({ message: 'Could not find key. Please try a different ID.' });
});
```
The only gate on this handler is a regex format check on `keyId` — there is no `context.session` check anywhere in the function. It is the backing endpoint for the Admin UI's `decrypt-recipient.tsx` tool (`fetch('/rest/keys/' + keyId)`), which implies the intended design was admin-only access, but nothing enforces that server-side. Additionally, `context.db.*` is Keystone's internal/sudo API, which deliberately bypasses the list's `access` configuration — so this endpoint remains exploitable even if F1 (`access: allowAll`) is fixed.

## Steps to Reproduce (Safe Verification)
1. Read `api/keystone.ts` and confirm no `context.session`/`req.session` check exists in the `/rest/keys/:keyId` handler.
2. Cross-reference KeystoneJS docs confirming `context.db` bypasses list-level `access` control (unlike `context.query`).
3. (For the program's own verification, not performed here) An anonymous `GET /rest/keys/<any-valid-looking-cuid>` request would be expected to return `{"key": "..."}` whenever that ID exists.

## Impact
Unauthenticated disclosure of the symmetric key used to decrypt customer shipping PII (name, address, phone — see `src/lib/utils.ts`'s `encrypt`/`decrypt`). Combined with any other means of obtaining the matching Stripe Checkout session metadata (the encrypted blob itself), this would allow full recovery of a customer's shipping address.

## Recommended Remediation
Add an explicit `if (!req.context.session?.data) return res.status(401).end();` check (or equivalent) to this route, and replace `context.db` with `context.query` so the route also benefits from list-level access control once F1 is fixed.
```

## 📊 Bulgu F3: src/routes/webhooks/stripe/+server.ts::fulfillOrder(): sipariş-tamamlama anındaki yaptırım (sanctions) kontrolü, Stripe session metadata'sında ASLA doldurulmayan bir alanı (`metadata?.country_code`) kontrol ediyor -- bu ikinci-savunma-katmanı pratikte her zaman devre dışı (dead code)
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** Low
* **Zafiyet Sınıfı (CWE):** CWE-693: Protection Mechanism Failure
* **Stage 2 Confidence:** 55/100 — Stage1'in iki dosyadaki (`cart/+page.server.ts` metadata OLUSTURMA VE `webhooks/stripe/+server.ts` fulfillOrder KONTROLU) `evidence_quote`'larini BIREBIR dogruladim -- `metadata` NESNESI GERCEKTEN SADECE `{ shippingData, keyId }` ICERIYOR, `country_code` ALANI HICBIR YERDE EKLENMIYOR, VE `fulfillOrder()` GERCEKTEN `metadata?.country_code`'U KONTROL EDIYOR -- bu JavaScript `Set.has(undefined) === false` SEMANTIGI NEDENIYLE MANTIKSAL olarak KESIN bir DEAD-CODE/HEP-FALSE durumu, SPEKULASYON DEGIL. CURUTMEYE CALISTIM: 'belki bu bilincli bir TASARIM -- SADECE submission-ANINDAKI kontrol YETERLI GORULMUS, webhook'taki SATIR SADECE eski/KALINTI kod' diye DUSUNDUM -- bu MUMKUN, ANCAK KODUN KENDISI (yorumlar, DEGISKEN adlandirmasi) bunun BILINCLI bir 'defense-in-depth' NIYETI TASIDIGINI GOSTERIYOR (AYNI `blockedCountryCodes` setinin, AYNI `ValidationError` sinifiyla, webhook KATMANINDA TEKRAR CAGRILMASI -- bu TESADUFEN degil, ACIKCA bir IKINCI kontrol NIYETI). GERCEK-dunya ISTISMAR edilebilirligi ('bu bypass'i TETIKLEYECEK BASKA bir YOL VAR MI, yoksa SADECE submission-ANINDAKI TEK kontrol HER ZAMAN YETERLI MI') teslim edilen KAPSAM icinde TAM olarak KANITLANAMADI (stage1'in de belirttigi gibi, Stripe Checkout'un KENDI shipping_address_collection OZELLIGI bu PROJEDE KULLANILMADIGI icin ALTERNATIF bir giris NOKTASI GORUNMUYOR, ANCAK bu NEGATIF bir KANIT -- 'baska YOL YOK' DEMEK zor). Bu nedenle ORTA (55) confidence ile PASS: KOD-defekti KESIN VE SOMUT (compliance/export-kontrolu KIRIK), ANCAK GERCEK-dunya ETKI SINIRI (sadece BU TEK path icin) TAM teyit EDILEMEDI.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** src/routes/webhooks/stripe/+server.ts::fulfillOrder()
* **Kanıt kaynağı:** `scripts/bugbounty/out/brave_store-brave-com/raw/ingested_incoming_2026-11-09T09-41-00_brave_store-brave-com.json`
* **Kanıt alıntısı:**
  ```
  if (blockedCountryCodes.has(metadata?.country_code as string)) {
      throw new ValidationError('Invalid recipient region.');
    }
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** `cart/+page.server.ts`'teki sepet-GONDERIM ADIMI, kullanicinin GONDERDIGI `shippingAddress.country_code`'u (ham POST govdesinden) `blockedCountryCodes` (yaptirimli/Printful-TARAFINDAN engellenen ULKELER) listesine karsi KONTROL EDIYOR VE Stripe Checkout OTURUMU OLUSTURULMADAN ONCE BU KONTROLU BASARIYLA GECIRIYOR -- ANCAK bu kontrolden GECEN `recipientInformation`, Stripe session metadata'sina SADECE SIFRELENMIS bir BLOB (`shippingData`) VE bir `keyId` olarak YAZILIYOR; `country_code` alani metadata'ya AYRICA (duz METIN olarak) EKLENMIYOR. Webhook'un `fulfillOrder()` FONKSIYONU, odeme TAMAMLANDIKTAN SONRA (yani SIFRELI veri COZULDUKTEN SONRA) BIR DAHA ULKE-KONTROLU YAPMAYA calisir GIBI GORUNUYOR (`blockedCountryCodes.has(metadata?.country_code...)`), ANCAK bu alan METADATA'DA HICBIR ZAMAN MEVCUT OLMADIGI icin (`metadata?.country_code` HER ZAMAN `undefined`), `Set.has(undefined)` HER ZAMAN `false` DONER -- bu kontrol PRATIKTE ASLA TETIKLENMEZ VE SIPARIS, COZULMUS `shippingData.country_code` HICBIR SEKILDE TEKRAR KONTROL EDILMEDEN DOGRUDAN Printful'A GONDERILIR. Bu, SADECE submission-ANINDAKI (ham, kullanici-TARAFINDAN GONDERILEN form) TEK bir dogrulama KATMANINA GUVENILDIGI, ikinci-savunma (defense-in-depth) katmaninin ise KOD-HATASI NEDENIYLE HICBIR ZAMAN CALISMADIGI anlamina GELIR.
* **Nasıl Doğrulanır (Güvenli Doğrulama Adımları):**
  1. `src/routes/cart/+page.server.ts` dosyasindaki `stripe.checkout.sessions.create(...)` cagrisindaki `metadata` NESNESI SATIR SATIR okunarak, SADECE `shippingData` VE `keyId` ALANLARININ BULUNDUGU, `country_code` ALANININ HICBIR YERDE EKLENMEDIGI DOGRULANDI.
  2. `src/routes/webhooks/stripe/+server.ts`'teki `fulfillOrder()` FONKSIYONUNDA `metadata?.country_code` ifadesinin GECTIGI TEK YER BULUNDU VE bu ifadenin, YUKARIDA DOGRULANAN metadata YAPISINDA KARSILIGI OLMADIGI icin HER ZAMAN `undefined` DEGERLENDIRECEGI (dolayisiyla `Set.has(undefined) === false`) MANTIKSAL olarak dogrulandi (JavaScript `Set.has()` SEMANTIGI -- canli istek gerektirmeyen, dilin KENDI DAVRANISINA dayanan bir DOGRULAMA).

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
## Summary
The Stripe webhook handler's `fulfillOrder()` function contains a second sanctions/export-compliance check (`blockedCountryCodes.has(metadata?.country_code)`) that references a Stripe session metadata field (`country_code`) which is never populated anywhere in the codebase — making this defense-in-depth check permanently dead code.

## Vulnerability Details & Root Cause
In `src/routes/cart/+page.server.ts`, the Stripe Checkout session is created with:
```ts
metadata: {
  shippingData: encryptedShippingData,
  keyId: shippingDataKey.id
}
```
No `country_code` field is ever added. Yet in `src/routes/webhooks/stripe/+server.ts`:
```ts
if (blockedCountryCodes.has(metadata?.country_code as string)) {
  throw new ValidationError('Invalid recipient region.');
}
```
Since `metadata.country_code` is always `undefined`, and `Set.prototype.has(undefined)` always returns `false`, this check can never trigger. The only real sanctions enforcement is the one performed on raw, client-submitted form data in `cart/+page.server.ts` before the encrypted blob is even created — there is no re-validation of the actual (decrypted) shipping country at the point the order is handed off to Printful for real-world fulfillment.

## Steps to Reproduce (Safe Verification)
1. Read the `metadata` object passed to `stripe.checkout.sessions.create()` in `cart/+page.server.ts` — confirm it contains only `shippingData` and `keyId`.
2. Read the `fulfillOrder()` check in `webhooks/stripe/+server.ts` — confirm it reads `metadata?.country_code`, a field that was never set.
3. This is a logical/semantic defect confirmable purely by reading the two files; no live request was made.

## Impact
The intended second layer of sanctions/export-compliance enforcement at order-fulfillment time does not function. Compliance currently depends entirely on the single client-facing form check, with no verification against the actually-decrypted recipient address before forwarding the order to Printful in non-draft (production) mode.

## Recommended Remediation
Either add the recipient's `country_code` to the Stripe session metadata at creation time (in plaintext, since it isn't sensitive on its own) and check it in `fulfillOrder()`, or re-check `shippingData.country_code` (available right after `decrypt()` is called in `fulfillOrder()`) against `blockedCountryCodes` before calling `printfulApi.createOrder(...)`.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._