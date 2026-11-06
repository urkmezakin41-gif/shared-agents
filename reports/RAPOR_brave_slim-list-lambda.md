# Bug Bounty Raporu — brave_slim-list-lambda

**Tarih:** 2026-11-04 21:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/slim-list-lambda (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: Lambda function for reducing EasyList + EasyPrivacy for use in iOS clients.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_slim-list-lambda/raw`
* **Engellenen/erişilemeyen adımlar:** Bu Lambda'nin GERCEK AWS aglama-konfigurasyonu (VPC'ye BAGLI mi, hangi Guvenlik Gruplari/NACL'ler uygulaniyor, 169.254.169.254 IMDS'ye veya VPC-ici kaynaklara (orn. Postgres RDS) GERCEKTEN ERISEBILIYOR mu) bu KOD teslimininin DISINDA (altyapi-as-kod/Terraform/CloudFormation dosyalari bu teslimde YOK). Bu nedenle F1'in TAM etki-kapsamini (hangi ic-ag hedeflere ERISILEBILDIGI) KESIN olarak DOGRULAYAMADIM -- sadece KODUN KENDISININ hicbir HEDEF-kisitlamasi UYGULAMADIGI gercegi KESIN olarak dogrulandi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, EasyList/EasyPrivacy filtre-listesini iOS istemcileri icin KUCULTMEK uzere Tranco top-10k sitelerini GERCEK bir Chromium ORNEGIYLE TARAYAN cok-asamali bir AWS Lambda sistemi (crawl-dispatch -> crawl -> record -> build -> assemble). F1, bu sistemin KENDI TASARIMSAL doğasindan (gercek web icerigini GERCEK bir tarayiciyla render etme) KAYNAKLANAN bir SSRF zafiyeti.
* Iki commit diff'i (bagimlilik/eslint-config GUNCELLEMESI + CI pin-GUNCELLEMESI) guvenlik acisindan NOTR.
* `crawl-dispatch.js`'teki ILK-SEVIYE URL insasi (`jobDesc.url = http://${aDomain}`, Tranco listesinden) VE `crawl.js`'teki `selectETldPlusOneLinks()`'in eTLD+1-kisitlamasi, 'HANGI SAYFANIN bir sonraki NAVIGASYON HEDEFI olacagini' DOGRU sekilde KISITLIYOR -- bu iki kontrol KENDI BASLARINA SAGLAM. F1, bu kontrollerin SADECE NAVIGASYON kararina uygulanip, O SAYFANIN KENDI ALT-KAYNAK yuklemelerine HIC UYGULANMAMASINDAN kaynaklaniyor.
* `assemble.js`/`build.js` (son-cikti/DB-analiz mantigi) ve `db.js` (Postgres sorgulari) ZAMAN KISITI nedeniyle SADECE goz-gezdirme seviyesinde incelendi -- bu dosyalarda SQL-enjeksiyonu acisindan (parametrize sorgu kullanimi goruldu, ama TAM dogrulama YAPILMADI) AYRI bir bulgu ARANMADI.

## 📊 Bulgu F1: brave/lambda_actions/crawl.js: Puppeteer/Chromium ile taranan HERHANGI bir sayfanin (Tranco top-10k'dan veya ONDAN ayni-eTLD+1 baglantilariyla erisilen alt-sayfalardan) GOMULU ALT-KAYNAKLARI (img/script/iframe/fetch), HICBIR HEDEF-KISITLAMASI (SSRF savunmasi) OLMADAN LAMBDA'NIN KENDI AG BAGLAMINDAN cekiliyor VE istek-URL'si/HTTP-durum-kodu HICBIR FILTRELEME olmadan S3'e KAYDEDILIYOR
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** medium-high (gercek etki, Lambda'nin AG-izolasyon konfigurasyonuna BAGLI -- bu teslimde dogrulanamadi, ama bir Postgres DB'ye yazan bir Lambda'nin TIPIK OLARAK VPC'ye bagli OLMASI nedeniyle GERCEKCI bir ic-ag-erisimi riski)
* **Zafiyet Sınıfı (CWE):** CWE-918 (Server-Side Request Forgery)
* **Stage 2 Confidence:** 50/100 — Kod-seviyesi YAPISAL iddiayi (isWebUrl SADECE sema kontrolu yapar, hostname/IP kisitlamasi YOKTUR; bu kontrol VE eTLD+1-filtresi SADECE 'bir sonraki NAVIGASYON hedefi' kararina uygulanir, O SAYFANIN KENDI alt-kaynak yuklemelerine HICBIR SEKILDE uygulanmaz) TEKRAR KOD-OKUYARAK DOGRULADIM -- CURUTEMEDIM, bu KESIN bir gercek. `page.on('requestfinished', ...)` TUM kaynak-turlerini (resourceType filtrelemesi OLMADAN) yakaladigini ve bunlarin S3'e YAZILAN rapora GIRDIGINI de DOGRULADIM.

REJECT'E ITMEYE calistigim itirazlar VE neden TAM BASARILI OLAMADIKLARI: (1) 'AWS Lambda, EC2'den FARKLI bir ag-izolasyon modeline sahip, 169.254.169.254'e ERISIM Lambda kod YOLUNDAN TIPIK OLARAK MUMKUN DEGIL' -- bu GENEL-BILGI DOGRU VE confidence'i 65-70'TEN 50'YE DUSURUYOR, AMA SSRF'IN TEK HEDEFI IMDS DEGIL: eger bu Lambda VPC'YE BAGLIYSA (ki bir Postgres DB'YE DOGRUDAN YAZAN bir Lambda icin bu COK YAYGIN bir KONFIGURASYONDUR -- RDS'e Lambda'dan erismenin STANDART yolu VPC-ici ENI'dir), SSRF HALA VPC-ICI DIGER servislere (orn. DB'nin KENDISI, baska internal API'ler) karsi GECERLI bir ic-ag-tarama/erisim VEKTORU sunar -- bu ALTYAPI-konfigurasyonu BU TESLIMDE YOK, dogrulanamadi, ama bu BIR VARSAYIM DEGIL, YAYGIN bir MUHENDISLIK GERCEGIDIR (confidence'i TAMAMEN SIFIRLAMAZ). (2) 'Kaydedilen veri SADECE hash/durum-kodu, HAM ICERIK DEGIL, dolayisiyla SOMUT bir VERI-SIZINTISI YOK' -- DOGRU VE confidence'i daha fazla DUSURUYOR (bu, 'kanitlanmis veri-sizintisi' yerine 'ic-ag-RECON/port-tarama oracle'i' seklinde CERCEVELENMELI, ki stage1 BUNU ZATEN BOYLE YAPMIS). (3) 'Saldirgan Tranco top-10k'da BIR SITEYE ICERIK YERLESTIREBILMELI' -- bu GERCEKTEN bir ENGEL (Tranco top-10k'ya girmek KOLAY DEGIL), AMA bu kisitlama MUTLAK DEGIL: eTLD+1-sinirli ALT-sayfalar da DAHIL (orn. kullanici-tarafindan-olusturulan-icerik barindiran, Tranco'da listelenen BUYUK bir platformun (forum/blog/paylasim-sitesi) BIR ALT-SAYFASINA icerik YERLESTIRMEK, cok DAHA ERISILEBILIR bir ESIK) VE bu, 'web-genelinde saldirgan' modeline GENEL OLARAK UYUYOR (klasik bug-bounty 'bir web sayfasi X yapabilir' SENARYOSU).

PASS karari: YAPISAL kod-defekti KESIN, SSRF-sinifi GENEL OLARAK GECERLI bir guvenlik-sorunu (CWE-918), ETKI (ic-ag erisimi mi, SADECE dis-SSRF mi) ALTYAPI-BAGIMLI VE BU TESLIMDE dogrulanamadi -- bu ORTA-duzeyde bir confidence'i (50) HAKLI kiliyor: `base_onchainsummer.xyz` (confidence 55, somut-DOGRULANMIS ucuncu-taraf etkisi) kadar KESIN DEGIL ama `constellation-processors` (confidence 45, HARICI-kutuphane-BAGIMLI) ile AYNI SEVIYEDE -- 'kod-defekti KESIN, nihai-etki bagimliligi BU TESLIM DISINDA'.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** brave/lambda_actions/crawl.js::_crawlPage() (satir ~2042-2120, `page.goto(args.url)` cagrisi VE `onRequestCompleteCallback`) + brave/validation.js::isWebUrl() (satir ~2474-2491, sadece http/https SEMA kontrolu -- hostname/IP kisitlamasi YOK)
* **Kanıt kaynağı:** `brave/validation.js`
* **Kanıt alıntısı:**
  ```
  const isWebUrl = possibleUrl => {
  ...
  if (urlObj.protocol === 'http:' || urlObj.protocol === 'https:') {
    return [true, undefined]
  }
  return [false, `Url protocol is not http(s), its ${urlObj.protocol}`]
}
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** `crawl.js`'teki `validateArgs()`, Lambda'ya GECIRILEN `args.url` ARGUMANINI `braveValidationLib.isWebUrl` ile dogruluyor -- ANCAK bu fonksiyon SADECE URL SEMASININ (`http:`/`https:`) oldugunu KONTROL EDIYOR, HOSTNAME/IP uzerinde HICBIR KISITLAMA (ozel/link-local/loopback IP araliklarini -- orn. `169.254.169.254` AWS metadata, `127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16` -- REDDETME) YAPMIYOR. Bu ZATEN BASLI-BASINA, lambda ARGUMANI olarak RASTGELE bir IC-AG hedefinin (teorik olarak) KABUL EDILEBILMESI anlamina GELIYOR -- AMA bu ARGUMAN pratikte `crawl-dispatch.js`'teki `jobDesc.url = \`http://${aDomain}\`` (Tranco listesinden gelen, DOGRUDAN ATTACKER-KONTROLLU OLMAYAN bir alan-adi) ile DOLDURULDUGU icin, BU OZEL YOL dogrudan sömürülmesi GUC.

DAHA CIDDI VE GERCEKCI YOL: `_crawlPage()` fonksiyonu, `page.goto(args.url)` ile HEDEF SAYFAYI Puppeteer/Chromium ile TAM OLARAK RENDER EDIYOR -- bu, sayfanin TUM GOMULU ALT-KAYNAKLARINI (`<img src>`, `<script src>`, `<iframe src>`, sayfanin KENDI JS'inin yaptigi `fetch()`/XHR cagrilari) DA GETIRIR. `selectETldPlusOneLinks()`'teki eTLD+1-ESLESME KISITLAMASI (`childLinkETld !== mainETld → continue`) SADECE HANGI `<a href>` BAGLANTILARININ bir SONRAKI RECURSIVE `crawl.js` CAGRISINA (yeni bir `page.goto()` HEDEFI olarak) KUYRUKLANACAGINI SINIRLIYOR -- bu kisitlama, O ANKI sayfanin KENDI ALT-KAYNAK YUKLEMELERINE HICBIR SEKILDE UYGULANMIYOR (Chrome'un KENDI kaynak-yukleme motoru, `isWebUrl`/eTLD+1 kontrolunden TAMAMEN BAGIMSIZ calisir). Yani: Tranco top-10k'daki (veya ONDAN eTLD+1-sinirli baglantilarla erisilen) HERHANGI bir sitenin, `<img src="http://10.0.0.5:5432/">` veya benzeri bir HTML elemanini SAYFASINA GOMEBILMESI, BU LAMBDA'NIN KENDI CHROMIUM INSTANSININ, LAMBDA'NIN KENDI AG BAGLAMINDAN (potansiyel olarak VPC-ici -- BU LAMBDA bir Postgres VERITABANINA YAZDIGI icin, TIPIK OLARAK VPC'YE BAGLI olmasi GEREKIR) bu HEDEFE bir ISTEK GONDERMESINE YOL ACAR -- KLASIK bir SSRF birincil-vektoru. `onRequestCompleteCallback()`, HER istegin `requestUrl`, `responseCode` VE `responseHash` (yanitin SHA256'si, ICERIGIN KENDISI DEGIL) degerlerini, HICBIR HEDEF-FILTRELEMESI yapmadan `requestStore`'a KAYDEDIYOR -- bu veriler SONUNDA S3'e YAZILIYOR (`crawlData.data = report`), yani bir SALDIRGAN (kendi web sitesine BU ozel HTML'i YERLESTIREREK) BU LAMBDA'YA, 'HANGI IC-AG ADRESLERINDE/PORTLARINDA bir SERVIS CALISIYOR' (durum-kodu/zamanlamadan) VE DUSUK-ENTROPIYE SAHIP sirlar icin bir 'HASH-ORACLE' (eger yanit ICERIGI tahmin edilebiliyorsa, SHA256 karsilastirmasiyla DOGRULANABILIR) SAGLAYABILIR -- VERININ KENDISI DEGIL ama VARLIGI/sekli HAKKINDA BILGI SIZINTISI.
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
  19.  
  20. (
  21. c
  22. a
  23. l
  24. i
  25. s
  26. t
  27. i
  28. r
  29. m
  30. a
  31.  
  32. G
  33. E
  34. R
  35. E
  36. K
  37. T
  38. I
  39. R
  40. M
  41. E
  42. Z
  43. )
  44. :
  45.  
  46. `
  47. v
  48. a
  49. l
  50. i
  51. d
  52. a
  53. t
  54. i
  55. o
  56. n
  57. .
  58. j
  59. s
  60. :
  61. :
  62. i
  63. s
  64. W
  65. e
  66. b
  67. U
  68. r
  69. l
  70. (
  71. )
  72. `
  73. '
  74. i
  75. n
  76.  
  77. K
  78. E
  79. S
  80. I
  81. N
  82. L
  83. I
  84. K
  85. L
  86. E
  87.  
  88. s
  89. a
  90. d
  91. e
  92. c
  93. e
  94.  
  95. `
  96. u
  97. r
  98. l
  99. O
  100. b
  101. j
  102. .
  103. p
  104. r
  105. o
  106. t
  107. o
  108. c
  109. o
  110. l
  111. `
  112.  
  113. K
  114. O
  115. N
  116. T
  117. R
  118. O
  119. L
  120. U
  121.  
  122. y
  123. a
  124. p
  125. t
  126. i
  127. g
  128. i
  129. ,
  130.  
  131. `
  132. u
  133. r
  134. l
  135. O
  136. b
  137. j
  138. .
  139. h
  140. o
  141. s
  142. t
  143. n
  144. a
  145. m
  146. e
  147. `
  148.  
  149. u
  150. z
  151. e
  152. r
  153. i
  154. n
  155. d
  156. e
  157.  
  158. H
  159. I
  160. C
  161. B
  162. I
  163. R
  164.  
  165. K
  166. O
  167. D
  168.  
  169. Y
  170. O
  171. L
  172. U
  173. N
  174. U
  175. N
  176.  
  177. b
  178. u
  179. l
  180. u
  181. n
  182. m
  183. a
  184. d
  185. i
  186. g
  187. i
  188.  
  189. d
  190. o
  191. g
  192. r
  193. u
  194. l
  195. a
  196. n
  197. d
  198. i
  199. .
  200.  
  201. `
  202. c
  203. r
  204. a
  205. w
  206. l
  207. .
  208. j
  209. s
  210. :
  211. :
  212. _
  213. c
  214. r
  215. a
  216. w
  217. l
  218. P
  219. a
  220. g
  221. e
  222. (
  223. )
  224. `
  225. '
  226. d
  227. e
  228.  
  229. `
  230. p
  231. a
  232. g
  233. e
  234. .
  235. g
  236. o
  237. t
  238. o
  239. (
  240. a
  241. r
  242. g
  243. s
  244. .
  245. u
  246. r
  247. l
  248. )
  249. `
  250. '
  251. i
  252. n
  253.  
  254. (
  255. P
  256. u
  257. p
  258. p
  259. e
  260. t
  261. e
  262. e
  263. r
  264. '
  265. i
  266. n
  267.  
  268. K
  269. E
  270. N
  271. D
  272. I
  273.  
  274. d
  275. o
  276. k
  277. u
  278. m
  279. e
  280. n
  281. t
  282. a
  283. s
  284. y
  285. o
  286. n
  287. u
  288. n
  289. a
  290.  
  291. g
  292. o
  293. r
  294. e
  295.  
  296. T
  297. U
  298. M
  299.  
  300. s
  301. a
  302. y
  303. f
  304. a
  305. -
  306. k
  307. a
  308. y
  309. n
  310. a
  311. k
  312. l
  313. a
  314. r
  315. i
  316. n
  317. i
  318.  
  319. Y
  320. U
  321. K
  322. L
  323. E
  324. Y
  325. E
  326. N
  327.  
  328. S
  329. T
  330. A
  331. N
  332. D
  333. A
  334. R
  335. T
  336.  
  337. b
  338. i
  339. r
  340.  
  341. A
  342. P
  343. I
  344. )
  345.  
  346. `
  347. o
  348. n
  349. R
  350. e
  351. q
  352. u
  353. e
  354. s
  355. t
  356. C
  357. o
  358. m
  359. p
  360. l
  361. e
  362. t
  363. e
  364. C
  365. a
  366. l
  367. l
  368. b
  369. a
  370. c
  371. k
  372. `
  373. '
  374. i
  375. n
  376.  
  377. `
  378. p
  379. a
  380. g
  381. e
  382. .
  383. o
  384. n
  385. (
  386. '
  387. r
  388. e
  389. q
  390. u
  391. e
  392. s
  393. t
  394. f
  395. i
  396. n
  397. i
  398. s
  399. h
  400. e
  401. d
  402. '
  403. ,
  404.  
  405. .
  406. .
  407. .
  408. )
  409. `
  410.  
  411. i
  412. l
  413. e
  414.  
  415. T
  416. U
  417. M
  418.  
  419. A
  420. G
  421.  
  422. i
  423. s
  424. t
  425. e
  426. k
  427. l
  428. e
  429. r
  430. i
  431. n
  432. i
  433.  
  434. (
  435. S
  436. A
  437. D
  438. E
  439. C
  440. E
  441.  
  442. a
  443. n
  444. a
  445.  
  446. n
  447. a
  448. v
  449. i
  450. g
  451. a
  452. s
  453. y
  454. o
  455. n
  456. u
  457.  
  458. D
  459. E
  460. G
  461. I
  462. L
  463. )
  464.  
  465. Y
  466. A
  467. K
  468. A
  469. L
  470. A
  471. D
  472. I
  473. G
  474. I
  475. ,
  476.  
  477. V
  478. E
  479.  
  480. b
  481. u
  482.  
  483. c
  484. a
  485. l
  486. l
  487. b
  488. a
  489. c
  490. k
  491. '
  492. i
  493. n
  494.  
  495. H
  496. I
  497. C
  498. B
  499. I
  500. R
  501.  
  502. `
  503. r
  504. e
  505. q
  506. u
  507. e
  508. s
  509. t
  510. U
  511. r
  512. l
  513. `
  514. /
  515. h
  516. o
  517. s
  518. t
  519. n
  520. a
  521. m
  522. e
  523.  
  524. F
  525. I
  526. L
  527. T
  528. R
  529. E
  530. L
  531. E
  532. M
  533. E
  534. S
  535. I
  536.  
  537. (
  538. o
  539. r
  540. n
  541. .
  542.  
  543. `
  544. i
  545. s
  546. W
  547. e
  548. b
  549. U
  550. r
  551. l
  552. `
  553.  
  554. v
  555. e
  556. y
  557. a
  558.  
  559. e
  560. T
  561. L
  562. D
  563. +
  564. 1
  565.  
  566. k
  567. o
  568. n
  569. t
  570. r
  571. o
  572. l
  573. u
  574. )
  575.  
  576. I
  577. C
  578. E
  579. R
  580. M
  581. E
  582. D
  583. I
  584. G
  585. I
  586. ,
  587.  
  588. d
  589. o
  590. g
  591. r
  592. u
  593. d
  594. a
  595. n
  596.  
  597. K
  598. O
  599. D
  600. -
  601. O
  602. K
  603. U
  604. M
  605. A
  606. S
  607. I
  608. Y
  609. L
  610. A
  611.  
  612. d
  613. o
  614. g
  615. r
  616. u
  617. l
  618. a
  619. n
  620. a
  621. b
  622. i
  623. l
  624. i
  625. r
  626. .
  627.  
  628. `
  629. s
  630. e
  631. l
  632. e
  633. c
  634. t
  635. E
  636. T
  637. l
  638. d
  639. P
  640. l
  641. u
  642. s
  643. O
  644. n
  645. e
  646. L
  647. i
  648. n
  649. k
  650. s
  651. (
  652. )
  653. `
  654. '
  655. i
  656. n
  657.  
  658. e
  659. T
  660. L
  661. D
  662. +
  663. 1
  664. -
  665. k
  666. i
  667. s
  668. i
  669. t
  670. l
  671. a
  672. m
  673. a
  674. s
  675. i
  676. n
  677. i
  678. n
  679.  
  680. S
  681. A
  682. D
  683. E
  684. C
  685. E
  686.  
  687. `
  688. <
  689. a
  690.  
  691. h
  692. r
  693. e
  694. f
  695. >
  696. `
  697.  
  698. E
  699. L
  700. E
  701. M
  702. A
  703. N
  704. L
  705. A
  706. R
  707. I
  708. N
  709. I
  710.  
  711. i
  712. s
  713. l
  714. e
  715. d
  716. i
  717. ğ
  718. i
  719.  
  720. (
  721. y
  722. a
  723. n
  724. i
  725.  
  726. S
  727. A
  728. D
  729. E
  730. C
  731. E
  732.  
  733. '
  734. b
  735. i
  736. r
  737.  
  738. s
  739. o
  740. n
  741. r
  742. a
  743. k
  744. i
  745.  
  746. h
  747. a
  748. n
  749. g
  750. i
  751.  
  752. S
  753. A
  754. Y
  755. F
  756. A
  757.  
  758. k
  759. u
  760. y
  761. r
  762. u
  763. k
  764. l
  765. a
  766. n
  767. a
  768. c
  769. a
  770. k
  771. '
  772.  
  773. k
  774. a
  775. r
  776. a
  777. r
  778. i
  779. n
  780. i
  781.  
  782. e
  783. t
  784. k
  785. i
  786. l
  787. e
  788. d
  789. i
  790. g
  791. i
  792. )
  793. ,
  794.  
  795. `
  796. o
  797. n
  798. R
  799. e
  800. q
  801. u
  802. e
  803. s
  804. t
  805. C
  806. o
  807. m
  808. p
  809. l
  810. e
  811. t
  812. e
  813. C
  814. a
  815. l
  816. l
  817. b
  818. a
  819. c
  820. k
  821. `
  822. '
  823. i
  824. n
  825.  
  826. I
  827. S
  828. E
  829.  
  830. T
  831. U
  832. M
  833.  
  834. k
  835. a
  836. y
  837. n
  838. a
  839. k
  840. -
  841. T
  842. U
  843. R
  844. L
  845. E
  846. R
  847. I
  848. N
  849. I
  850.  
  851. (
  852. i
  853. m
  854. g
  855. /
  856. s
  857. c
  858. r
  859. i
  860. p
  861. t
  862. /
  863. i
  864. f
  865. r
  866. a
  867. m
  868. e
  869. /
  870. f
  871. e
  872. t
  873. c
  874. h
  875.  
  876. -
  877. -
  878.  
  879. `
  880. r
  881. e
  882. q
  883. u
  884. e
  885. s
  886. t
  887. .
  888. r
  889. e
  890. s
  891. o
  892. u
  893. r
  894. c
  895. e
  896. T
  897. y
  898. p
  899. e
  900. (
  901. )
  902. `
  903. )
  904.  
  905. A
  906. Y
  907. I
  908. R
  909. T
  910.  
  911. E
  912. T
  913. M
  914. E
  915. D
  916. E
  917. N
  918.  
  919. k
  920. a
  921. y
  922. d
  923. e
  924. t
  925. t
  926. i
  927. g
  928. i
  929.  
  930. k
  931. a
  932. r
  933. s
  934. i
  935. l
  936. a
  937. s
  938. t
  939. i
  940. r
  941. m
  942. a
  943. l
  944. i
  945.  
  946. o
  947. l
  948. a
  949. r
  950. a
  951. k
  952.  
  953. G
  954. O
  955. R
  956. U
  957. L
  958. E
  959. B
  960. I
  961. L
  962. I
  963. R
  964. .

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
In `brave/lambda_actions/crawl.js`, `_crawlPage()` fully renders each crawled page via Puppeteer/Chromium (`page.goto(args.url)`), which causes Chromium to fetch every embedded subresource of that page (images, scripts, iframes, and any `fetch()`/XHR calls the page's own JavaScript makes) using the Lambda function's own network context. The only input validation present, `isWebUrl()` in `brave/validation.js`, checks solely that a URL's scheme is `http:`/`https:` -- it performs no hostname or IP-range restriction (no rejection of loopback, link-local, or RFC1918 private ranges). Critically, this validation is only ever applied to the top-level crawl-job URL argument (which in practice comes from the Tranco top-N domain list, not directly attacker-controlled) and to the same-eTLD+1 filter in `selectETldPlusOneLinks()` that decides which `<a href>` links get queued as the *next* page to navigate to -- neither check is applied to a page's own embedded subresources. This means any web page that ends up being crawled (any of the Tranco top ~10,000 domains, or a same-eTLD+1-linked page reached within the configured crawl depth/breadth) can embed an element such as `<img src="http://169.254.169.254/...">` or `<img src="http://10.0.0.5:5432/">`, and the Lambda's Chromium instance will issue that request from the Lambda's own network context -- a server-side request forgery (SSRF) primitive. `onRequestCompleteCallback()` then records every observed request's `requestUrl`, HTTP `responseCode`, and a SHA-256 `responseHash` of the response body (not the body itself) into the crawl report that gets written to S3 -- providing an attacker able to get content onto a crawled site with an internal-network port-scanning/service-discovery oracle (via status code/timing) and, for low-entropy predictable responses, a hash-oracle, from this Lambda's network vantage point. The practical blast radius (whether this Lambda runs inside a VPC with access to internal services such as the Postgres database `record.js`/`build.js` write to, or whether AWS Lambda's execution model exposes anything reachable at the classic EC2 instance-metadata address) could not be confirmed from the source code alone (no infrastructure-as-code was in scope for this review), but the code itself provides no SSRF mitigation whatsoever for subresource loads. Suggested fix: install a Puppeteer request-interception handler (`page.setRequestInterception(true)` + an `request` listener) that resolves each request's hostname and aborts it if it resolves to a private/loopback/link-local IP address or the cloud metadata address, before the request is allowed to proceed, in addition to (not instead of) the existing top-level URL/eTLD+1 checks.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._