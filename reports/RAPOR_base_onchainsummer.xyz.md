# Bug Bounty Raporu — base_onchainsummer.xyz

**Tarih:** 2026-11-03 18:41 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/onchainsummer.xyz (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_onchainsummer.xyz/raw`
* **Engellenen/erişilemeyen adımlar:** yok

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base'in 2023 'Onchain Summer' NFT kampanya web sitesi -- gercek backend API route'lari iceren bir Next.js uygulamasi (partner yonetimi, Reservoir NFT API proxy'si, Arweave/Mirror makale entegrasyonu, zamanlama).
* Son iki commit: (1) bir partner'in (Stand With Crypto) NFT drop'lari icin 'creator' cuzdan adresinin guncellenmesi -- salt yapilandirma verisi degisikligi, kod mantigi degil; (2) Farcaster Frame meta-veri destegi eklenmesi (@coinbase/onchainkit) -- yeni, katkili bir ozellik, guvenlik mantigi tasimiyor.
* F1 disinda, `api/partners/[slug]/audit/route.ts` ve `api/generateArweave/route.ts` DOGRU sekilde gizli bir `x-api-key` basligi (`process.env.OCS_API_KEY` ile karsilastirma) ile korunuyor -- bu, F1'deki Origin-tabanli kontrolden FARKLI olarak GERCEK bir sunucu-dogrulanmis gizli-anahtar kontrolu, saglam.
* `api/arweave/route.ts` (POST, kimliksiz) yalnizca KAMUYA ACIK Arweave/Mirror makale icerigini bir dijest-kimligiyle getiriyor -- `digestId` bir GraphQL degiskeni olarak kullaniliyor (ham URL enjeksiyonu degil), gizli bir kaynagi veya yazma-islemini acikca EXPOSE etmiyor -- kasitli, kabul edilebilir bir tasarim.
* `api/generateArweave/route.ts`'in dosya-yazma islemi (`writeFile('./generated/arweave.ts', ...)`) SABIT-KODLANMIS bir yola yaziyor, kullanici girdisinden turetilmiyor -- path-traversal riski yok; zaten API-key ile korunuyor.
* Hata-isleme deseninde (`api/arweave/route.ts` ve `api/partners/[slug]/audit/route.ts`) hata YIGIN IZLERININ (`error.stack`) istemciye JSON yaniti icinde dondurulmesi KUCUK bir bilgi-sizdirma gozlemidir -- ancak audit route zaten API-key korumali, arweave route'u ise yalnizca KAMUYA ACIK veri getiriyor, bu nedenle bu gozlem ayri bir bulgu olarak RAPORLANMADI (dusuk deger, F1'in notlarina dahil edildi).
* SONUC: Bir gercek, orta-siddette erisim-kontrolu bulgusu (F1, spoofable Origin/Referer tabanli kotuye-kullanim onleme) disinda, HackerOne-raporlanabilir baska bir guvenlik acigi TESPIT EDILEMEDI.

## 📊 Bulgu F1: api/reservoir proxy: erisim kontrolu sahteciligi-mumkun Origin/Referer basliklarina dayaniyor -- paralı Reservoir API anahtari herkesce acik-proxy olarak kotuye kullanilabilir
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** medium
* **Zafiyet Sınıfı (CWE):** CWE-346 (Origin Validation Error) / CWE-290 (Authentication Bypass by Spoofing)
* **Stage 2 Confidence:** 55/100 — F1'i curutmeye calisirken dogrulanan gercekler bulguyu GUCLENDIRIYOR, zayiflatmiyor: (1) Origin/Referer/Host basliklarinin herhangi bir HTTP istemcisi (tarayici DISI) tarafindan OZGURCE ayarlanabildigi, HTTP protokolunun TEMEL bir gercegi -- CORS/SOP yalnizca TARAYICI-tarafli ISTEMCI DAVRANISINI kisitlar, sunucu-tarafi bir dogrulama DEGILDIR. (2) Eger `ALLOWED_API_DOMAINS` ortam degiskeni HIC ayarlanmamissa, kod `if (allowedDomains && allowedDomains.length > 0)` kontrolu ile TUM kontrolu ATLAR -- proxy TAMAMEN ACIK olur (bu durumda bile bulgu gecerli, sadece 'bypass' adimi gereksiz hale gelir). (3) Bu, Coinbase/Base'in KENDI parali ucuncu-taraf (Reservoir) API anahtarinin IZINSIZ kullanimina/tuketimine izin veren GERCEK bir ucuncu-taraf-kotuye-kullanim senaryosu -- 'kendi kendine zarar' sinifindaki onceki dusuk-guvenli bulgulardan (orn. base_benchmark/base_eip712sign) FARKLI olarak, burada GERCEK bir UCUNCU TARAF (herhangi bir internet kullanicisi) sitenin odedigi bir kaynagi istismar edebiliyor, kendi kaynagini degil. Bu, CWE-346/CWE-290 siniflandirmasina uyan, bug-bounty programlarinin SIKCA odullendirdigi bir kalip ('API key proxy abuse via spoofable header-based access control'). Confidence orta-seviyede (55) tutuluyor cunku: (a) GERCEK saldiri trafigi gonderilmedi (pipeline kurallari geregi canli test yapilmadi, bu TAMAMEN statik kod analizine dayaniyor), (b) `ALLOWED_API_DOMAINS`'in PRODUCTION'da GERCEKTE ayarlanip ayarlanmadigi/hangi deger(ler)le ayarlandigi bilinmiyor (missing context -- deployment config), ve (c) 2023 kampanyasina ait, muhtemelen artik az trafikli bir site oldugu icin GERCEK is-etkisi (maliyet/kota tuketimi) sinirli olabilir -- ancak kod-seviyesindeki ZAYIFLIK kesin ve dogrulanmis.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** src/app/api/reservoir/[...slug]/route.ts, fonksiyon proxy()
* **Kanıt kaynağı:** `src/app/api/reservoir/[...slug]/route.ts`
* **Kanıt alıntısı:**
  ```
  let origin =
      reqHeaders.get('origin') ||
      reqHeaders.get('referer') ||
      reqHeaders.get('host') ||
      ''
    ...
    if (!origin.length || !allowedDomains.includes(origin)) {
      return NextResponse.json({ error: 'Access forbidden' }, { status: 403 })
    }
    ...
    if (process.env.RESERVOIR_API_KEY)
      headers.set('x-api-key', process.env.RESERVOIR_API_KEY)
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** Bu proxy, `/api/reservoir/*` isteklerini `https://api-base.reservoir.tools/{endpoint}`'e yonlendirip SUNUCU-TARAFI gizli `RESERVOIR_API_KEY`'i ekliyor -- amac (yorumda belirtildigi gibi) 'the Reservoir API key is not exposed to the client' -- yani anahtar gercekten ISTEMCIYE SIZDIRILMIYOR (yalnizca upstream'e gonderiliyor). ANCAK, bu endpoint'e erisimi kontrol eden TEK mekanizma `Origin`/`Referer`/`Host` basliklarinin `ALLOWED_API_DOMAINS` listesinde olup olmadigini kontrol etmek. Bu basliklar TARAYICI-tarafindan GUVENILIR sekilde ayarlanir (CORS/SOP kurallari), ANCAK dogrudan bir HTTP istemcisi (curl, Python requests, bir sunucu-tarafi script) BU BASLIKLARI HERHANGI bir deger ile OZGURCE AYARLAYABILIR -- sunucu tarafinda bu baslik degerlerini DOGRULAYAN (orn. bir imza, bir gizli token, bir CORS-preflight zorunlulugu) HICBIR EK mekanizma YOK. Bu nedenle, `ALLOWED_API_DOMAINS` ortam degiskeni ayarlanmis olsa BILE, bu kontrol tarayici-disi herhangi bir istemci tarafindan trivial sekilde atlanabilir (`Origin: <allowed-domain>` basligini elle ekleyerek).
* **Nasıl Doğrulanır (Güvenli Doğrulama Adımları):**
  1. S
  2. t
  3. a
  4. t
  5. i
  6. k
  7.  
  8. k
  9. o
  10. d
  11.  
  12. o
  13. k
  14. u
  15. m
  16. a
  17. s
  18. i
  19. :
  20.  
  21. `
  22. a
  23. l
  24. l
  25. o
  26. w
  27. e
  28. d
  29. D
  30. o
  31. m
  32. a
  33. i
  34. n
  35. s
  36. `
  37.  
  38. k
  39. o
  40. n
  41. t
  42. r
  43. o
  44. l
  45. u
  46. n
  47. u
  48. n
  49.  
  50. S
  51. A
  52. D
  53. E
  54. C
  55. E
  56.  
  57. `
  58. r
  59. e
  60. q
  61. H
  62. e
  63. a
  64. d
  65. e
  66. r
  67. s
  68. .
  69. g
  70. e
  71. t
  72. (
  73. '
  74. o
  75. r
  76. i
  77. g
  78. i
  79. n
  80. '
  81. )
  82. `
  83. /
  84. `
  85. r
  86. e
  87. f
  88. e
  89. r
  90. e
  91. r
  92. `
  93. /
  94. `
  95. h
  96. o
  97. s
  98. t
  99. `
  100.  
  101. d
  102. e
  103. g
  104. e
  105. r
  106. l
  107. e
  108. r
  109. i
  110. n
  111. e
  112.  
  113. b
  114. a
  115. k
  116. i
  117. p
  118.  
  119. b
  120. u
  121. n
  122. l
  123. a
  124. r
  125. i
  126.  
  127. b
  128. i
  129. r
  130.  
  131. i
  132. z
  133. i
  134. n
  135. -
  136. l
  137. i
  138. s
  139. t
  140. e
  141. s
  142. i
  143. y
  144. l
  145. e
  146.  
  147. k
  148. a
  149. r
  150. s
  151. i
  152. l
  153. a
  154. s
  155. t
  156. i
  157. r
  158. d
  159. i
  160. g
  161. i
  162. ,
  163.  
  164. v
  165. e
  166.  
  167. b
  168. u
  169.  
  170. d
  171. e
  172. g
  173. e
  174. r
  175. l
  176. e
  177. r
  178. i
  179. n
  180.  
  181. s
  182. u
  183. n
  184. u
  185. c
  186. u
  187.  
  188. t
  189. a
  190. r
  191. a
  192. f
  193. i
  194. n
  195. d
  196. a
  197. n
  198.  
  199. K
  200. R
  201. I
  202. P
  203. T
  204. O
  205. G
  206. R
  207. A
  208. F
  209. I
  210. K
  211.  
  212. o
  213. l
  214. a
  215. r
  216. a
  217. k
  218.  
  219. d
  220. o
  221. g
  222. r
  223. u
  224. l
  225. a
  226. n
  227. m
  228. a
  229. d
  230. i
  231. g
  232. i
  233.  
  234. (
  235. i
  236. m
  237. z
  238. a
  239. ,
  240.  
  241. n
  242. o
  243. n
  244. c
  245. e
  246. ,
  247.  
  248. v
  249. e
  250. y
  251. a
  252.  
  253. s
  254. u
  255. n
  256. u
  257. c
  258. u
  259. -
  260. t
  261. a
  262. r
  263. a
  264. f
  265.  
  266. C
  267. O
  268. R
  269. S
  270. -
  271. z
  272. o
  273. r
  274. u
  275. n
  276. l
  277. u
  278. -
  279. t
  280. a
  281. r
  282. a
  283. y
  284. i
  285. c
  286. i
  287. -
  288. d
  289. a
  290. v
  291. r
  292. a
  293. n
  294. i
  295. s
  296. i
  297. n
  298. a
  299.  
  300. g
  301. u
  302. v
  303. e
  304. n
  305.  
  306. D
  307. I
  308. S
  309. I
  310. N
  311. D
  312. A
  313.  
  314. b
  315. i
  316. r
  317.  
  318. m
  319. e
  320. k
  321. a
  322. n
  323. i
  324. z
  325. m
  326. a
  327. )
  328.  
  329. a
  330. c
  331. i
  332. k
  333. c
  334. a
  335.  
  336. g
  337. o
  338. r
  339. u
  340. l
  341. u
  342. y
  343. o
  344. r
  345. .
  346.  
  347. B
  348. u
  349. ,
  350.  
  351. H
  352. T
  353. T
  354. P
  355.  
  356. p
  357. r
  358. o
  359. t
  360. o
  361. k
  362. o
  363. l
  364. u
  365. n
  366. u
  367. n
  368.  
  369. k
  370. e
  371. n
  372. d
  373. i
  374. s
  375. i
  376. y
  377. l
  378. e
  379.  
  380. d
  381. o
  382. g
  383. r
  384. u
  385. l
  386. a
  387. n
  388. a
  389. n
  390.  
  391. b
  392. i
  393. r
  394.  
  395. g
  396. e
  397. r
  398. c
  399. e
  400. k
  401. :
  402.  
  403. O
  404. r
  405. i
  406. g
  407. i
  408. n
  409. /
  410. R
  411. e
  412. f
  413. e
  414. r
  415. e
  416. r
  417. /
  418. H
  419. o
  420. s
  421. t
  422.  
  423. b
  424. a
  425. s
  426. l
  427. i
  428. k
  429. l
  430. a
  431. r
  432. i
  433.  
  434. H
  435. E
  436. R
  437.  
  438. Z
  439. A
  440. M
  441. A
  442. N
  443.  
  444. i
  445. s
  446. t
  447. e
  448. m
  449. c
  450. i
  451.  
  452. t
  453. a
  454. r
  455. a
  456. f
  457. i
  458. n
  459. d
  460. a
  461. n
  462.  
  463. o
  464. z
  465. g
  466. u
  467. r
  468. c
  469. e
  470.  
  471. a
  472. y
  473. a
  474. r
  475. l
  476. a
  477. n
  478. a
  479. b
  480. i
  481. l
  482. i
  483. r
  484. ,
  485.  
  486. c
  487. a
  488. l
  489. i
  490. s
  491. t
  492. i
  493. r
  494. m
  495. a
  496.  
  497. g
  498. e
  499. r
  500. e
  501. k
  502. t
  503. i
  504. r
  505. m
  506. e
  507. z
  508. .

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
`src/app/api/reservoir/[...slug]/route.ts` proxies requests to `https://api-base.reservoir.tools/*`, attaching a server-side `RESERVOIR_API_KEY` secret so the key itself never reaches the client (confirmed -- the key is never echoed back). However, the ONLY access-control gate in front of this proxy is a check that the request's `Origin`/`Referer`/`Host` header (in that fallback order) matches an `ALLOWED_API_DOMAINS` allowlist. These headers are fully attacker-controlled for any non-browser HTTP client (curl, a script, a server-side bot) -- there is no additional server-verified secret (API key, signed token, session cookie) gating this endpoint. Any third party can therefore set `Origin: <an-allowed-domain>` and use this site's paid Reservoir API key as a free, unauthenticated proxy to query ANY endpoint on api-base.reservoir.tools (not limited to functionality the site itself exposes), at the site owner's expense (API quota/rate-limit/cost). Suggested fix: gate the proxy with a server-verified secret (e.g. a first-party session cookie, a signed request, or restrict to specific known upstream paths/methods actually used by the site) rather than relying on spoofable Origin/Referer/Host headers for authorization.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._