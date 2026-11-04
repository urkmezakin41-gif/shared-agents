# Bug Bounty Raporu — brave_pagegraph-crawl

**Tarih:** 2026-11-04 23:42 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/pagegraph-crawl (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: JavaScript. Description: Gather pagegraph data from all over the internet.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_pagegraph-crawl/raw`
* **Engellenen/erişilemeyen adımlar:** Bu aracin GERCEKTE Brave'in ARASTIRMA/uretim BORULARINDA HANGI `--recursive-depth` degeriyle (varsayilan `1` = recursion KAPALI, ama OPERATORUN acikca ARTIRABILECEGI bir deger) VE HANGI AG/ALTYAPI BAGLAMINDAN (operatorun KENDI makinesi mi, paylasimli bir ARASTIRMA sunucusu mu, ic-ag erisimi olan bir ORTAM mi) CALISTIRILDIGI bu teslimde YOK (orkestrasyon/dagitim betikleri/altyapi-kodu bu REPODA DEGIL). Bu nedenle F1'in GERCEK pratik SIKLIGI/etkisi TAM olarak dogrulanamadi -- SADECE aracin KENDI KODUNUN hicbir KISITLAMA UYGULAMADIGI KESIN olarak dogrulandi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in Chromium-tabanli (Brave Browser'in KENDI PageGraph-ozellikli DERLEMESI) sayfanin TAM DAVRANIS GRAFIGINI (network/DOM/script etkilesimleri) kaydetmek icin kullandigi bir KOMUT-SATIRI ARASTIRMA/tarama araci. Bu, bu oturumda ONCEDEN incelenen `brave_slim-list-lambda`'nin AYNI GENEL KALIBINA (Chromium-tabanli, gercek web icerigini ziyaret eden bir TARAMA ARACI) sahip, ancak FARKLI bir THREAT MODEL'de (OPERATOR-cagrilan BIR CLI araci, OTOMATIK bir aglanmis SERVIS DEGIL).
* Iki commit diff'i (SALT BAGIMLILIK-GUNCELLEMESI: `follow-redirects` paketinin surum ARTIRIMI) guvenlik acisindan NOTR.
* `src/brave/files.ts::createFilename()` (cikti dosya-adi OLUSTURMA) OZELLIKLE incelendi -- `String(url).replace(/[^\w]/g, '_')` TUM alfanumerik-OLMAYAN karakterleri ALT-CIZGIYE CEVIRIYOR, bu PATH-TRAVERSAL riskini ETKISIZ KILIYOR (ne `/` ne `.` ne `..` HAYATTA KALIYOR) -- GUVENLI.
* `src/brave/puppeteer.ts`'teki Chromium BASLATMA BAYRAKLARI (`--proxy-server`, `--extra-args`, `--extensions-path`, `--disable-setuid-sandbox`) TUMU OPERATORUN KENDI CLI-ARGUMANLARINDAN GELIYOR, taranan SAYFA ICERIGINDEN DEGIL -- bu nedenle bir SALDIRGANIN (taranan bir SITE araciligiyla) BU BAYRAKLARI ETKILEMESI icin BIR YOL BULUNAMADI.
* SONUC: F1, bu aracin KENDI TASARIMINDAKI (slim-list-lambda'NIN ZATEN sahip oldugu eTLD+1-kisitlamasiNIN BU ARACTA TAMAMEN EKSIK OLMASI) somut bir YAPISAL FARKLILIKTAN KAYNAKLANAN, GECERLI bir SSRF deseni.

## 📊 Bulgu F1: src/brave/page.ts::selectRandomChildUrl() + src/brave/crawl.ts::doCrawl(): recursive-depth > 1 ile calistirildiginda, taranan sayfadaki HERHANGI bir `<a href>` baglantisi (DOMAIN/eTLD KISITLAMASI OLMADAN) bir SONRAKI TOP-LEVEL navigasyon HEDEFI olarak SECILEBILIYOR -- bu, aracin GERCEK HTTP(S) KAYNAK sinirlamasi disinda HICBIR hedef-kisitlamasi OLMAYAN bir SSRF birincil-vektoru olusturuyor, VE sonuc sayfanin EKRAN GORUNTUSU/HAR-govdesi gibi GERCEK ICERIGI YAKALANABILIYOR (sadece bir hash/durum-kodu DEGIL)
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** medium-high (bu oturumda ONCEDEN raporlanan brave_slim-list-lambda/F1'den DAHA CIDDI: BURADA eTLD+1-kisitlamasi YOK VE GERCEK yanit-ICERIGI -- ekran goruntusu/HAR govdesi -- YAKALANABILIYOR, ama etki OPERATORUN `--recursive-depth` SECIMINE BAGLI -- varsayilan KAPALI)
* **Zafiyet Sınıfı (CWE):** CWE-918 (Server-Side Request Forgery)
* **Stage 2 Confidence:** 52/100 — Kod-seviyesi YAPISAL iddiayi (asHTTPUrl SADECE protokol-on-ekini kontrol EDER; selectRandomChildUrl HICBIR domain/eTLD KISITLAMASI UYGULAMAZ; secilen link DOGRUDAN bir sonraki page.goto() CAGRISININ argumani OLUR) TEKRAR KOD-OKUYARAK DOGRULADIM -- CURUTEMEDIM, bu KESIN. slim-list-lambda ile KARSILASTIRMALI OKUMA da DOGRU: O ARAC `tldjsLib.getDomain()` ile ETLD+1 KISITLAMASI UYGULARken, BU ARAC HICBIR ESDEGER KISITLAMA ICERMIYOR -- bu YAPISAL FARK GERCEK.

REJECT'E ITMEYE calistigim itirazlar: (1) 'Varsayilan recursive-depth=1, yani recursion KAPALI' -- DOGRU VE confidence'i 65-70'TEN 52'YE DUSURUYOR, AMA 'bir ARACIN varsayilan AYARI GUVENLI' OLMASI, 'BU ARAC o AYARI DEGISTIRMEDEN KULLANILDIGINDA GUVENSIZ' GERCEGINI SIFIRLAMAZ -- aracin KENDI ACIKLAMASI ('gather data from ALL OVER THE INTERNET', buyuk-olcekli/ARASTIRMA amaci) VE yardim-metninin recursion'u bir NET OZELLIK olarak SUNMASI, bunun GERCEKTEN KULLANILAN bir PARAMETRE OLDUGUNU DUSUNDURUYOR -- bu bir VARSAYIM ama MAKUL bir VARSAYIM (ayni tur 'opsiyonel-ama-gercekci-kullanim' MANTIGI, slim-list-lambda'nin KENDI depth/breadth PARAMETRELERININ crawl-dispatch.js TARAFINDAN ACIKCA DOLDURULMASIYLA TUTARLI). (2) 'Bu bir CLI araci, OPERATOR kendi HEDEFINI SECIYOR, dolayisiyla saldirgan MODELI YOK' -- KISMEN DOGRU AMA EKSIK: saldirgan MODELI, 'operatorun SECTIGI (veya OTOMATIK bir listeden gelen) HEDEF sitenin KENDISI (veya ONDAN rastgele-yuruyusle ERISILEN herhangi bir ARA sayfa) kotu-niyetli/ELE-GECIRILMIS olabilir' SEKLINDE -- bu, TAM OLARAK slim-list-lambda'da KULLANILAN AYNI saldirgan-modeli (Tranco'dan bir SITE), BURADA SADECE 'hangi SITELER taraniyor' sorusu farkli (BU ARAC icin spesifik DEGIL, ama AYNI GENEL TEHDIT SINIFI GECERLI).

PASS karari: YAPISAL kod-defekti KESIN VE slim-list-lambda'daki BENZER bulgudan DAHA CIDDI (domain-kisitlamasi TAMAMEN YOK + GERCEK ICERIK yakalanabiliyor), ancak NIHAI pratik-SIKLIK (recursive-depth'in GERCEKTE nasil KULLANILDIGI) bu teslimde dogrulanamadi -- bu, slim-list-lambda'nin confidence 50'siyle AYNI SEVIYEDE (52, HAFIFCE daha YUKSEK CUNKU kisitlama EKSIKLIGI DAHA KESIN/daha az ALTYAPI-BAGIMLI bir gerceğe DAYANIYOR).

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** src/brave/page.ts::selectRandomChildUrl() (satir ~3507-3536) + src/brave/crawl.ts::doCrawl() (satir ~3014-3053, `randomChildUrl` atamasi VE YENI `doCrawl(newArgs, ...)` cagrisi) + src/brave/checks.ts::asHTTPUrl() (satir ~2518-2529, SADECE sema kontrolu)
* **Kanıt kaynağı:** `src/brave/page.ts`
* **Kanıt alıntısı:**
  ```
  const links: URL[] = [];
  for (const link of rawLinks) {
    const hrefHandle = await link.getProperty("href");
    const hrefValue = await hrefHandle.jsonValue();
    try {
      const hrefUrl = asHTTPUrl(hrefValue.trim(), mainFrameUrl);
      if (hrefUrl === undefined) { continue; }
      links.push(hrefUrl);
    } catch { continue; }
  }
  const randomLink = links[Math.floor(Math.random() * links.length)];
  return randomLink;
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** `checks.ts::asHTTPUrl()`, bir URL'nin KABUL EDILEBILIR olup olmadigini SADECE `url.protocol.startsWith('http')` ILE kontrol EDIYOR -- HOSTNAME veya IP uzerinde HICBIR KISITLAMA (ozel/loopback/link-local IP araliklarini REDDETME) YOK. `selectRandomChildUrl()`, taranan sayfadaki TUM `<a href>` baglantilarini bu TEK kontrolden GECIRIP (herhangi bir DOMAIN/eTLD kisitlamasi UYGULAMADAN) rastgele BIRINI SECIYOR; bu secim, `crawl.ts::doCrawl()`'de `newArgs.url = randomChildUrl; ...; await doCrawl(newArgs, ...)` ile BIR SONRAKI RECURSIVE CAGRININ `urlToCrawl` ARGUMANI OLUYOR, YANI bu URL `page.goto(urlToCrawl, { waitUntil: 'domcontentloaded' })` ile TAM BIR TOP-LEVEL NAVIGASYON HEDEFI OLARAK KULLANILIYOR (slim-list-lambda'daki gibi SADECE bir ALT-KAYNAK YUKLEMESI DEGIL, TAM bir SAYFA-ZIYARETI). `--recursive-depth` (varsayilan `1`, yani KAPALI) 1'DEN BUYUK bir DEGERE AYARLANDIGINDA (aracin KENDI YARDIM metni 'choose a link at random on page and do another crawl to this depth' diyerek bunu ACIKCA bir OZELLIK olarak TANIMLIYOR, VE aracin ACIKLAMASI 'Gather pagegraph data from all over the internet' olarak, BUYUK-OLCEKLI/COK-SAYFALI taramayi ima EDIYOR), TARANAN HERHANGI bir sayfadaki (ILK hedef VEYA rasgele-yuruyusun ONCEKI adimlarinda ziyaret edilen ARA sayfalardan) BIR BAGLANTI `http://169.254.169.254/...`, `http://localhost:PORT/...`, veya herhangi bir IC-AG adresine YONLENDIRILEBILIR, VE ARAC bu HEDEFE TAM bir PAGE NAVIGATION yapar -- ARDINDAN `args.screenshot` acikken BU SAYFANIN bir EKRAN-GORUNTUSU, `args.storeHar`/`args.storeHarBody` acikken BU SAYFANIN HTTP ISTEK/YANIT ICERIGI (GOVDE DAHIL) DISKE KAYDEDILIR -- bu, slim-list-lambda'daki (SADECE bir SHA256-hash/durum-kodu KAYDEDEN) bulgudan DAHA DOGRUDAN bir VERI-YAKALAMA SONUCU verir: ic-ag kaynaginin GERCEK ICERIGI (sayfa GORUNTUSU/HTTP yanit GOVDESI) elde edilebilir.
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
  47. a
  48. s
  49. H
  50. T
  51. T
  52. P
  53. U
  54. r
  55. l
  56. (
  57. )
  58. `
  59. '
  60. i
  61. n
  62.  
  63. K
  64. E
  65. S
  66. I
  67. N
  68. L
  69. I
  70. K
  71. L
  72. E
  73.  
  74. `
  75. u
  76. r
  77. l
  78. .
  79. p
  80. r
  81. o
  82. t
  83. o
  84. c
  85. o
  86. l
  87. .
  88. s
  89. t
  90. a
  91. r
  92. t
  93. s
  94. W
  95. i
  96. t
  97. h
  98. (
  99. '
  100. h
  101. t
  102. t
  103. p
  104. '
  105. )
  106. `
  107.  
  108. D
  109. I
  110. S
  111. I
  112. N
  113. D
  114. A
  115.  
  116. H
  117. I
  118. C
  119. B
  120. I
  121. R
  122.  
  123. k
  124. o
  125. n
  126. t
  127. r
  128. o
  129. l
  130.  
  131. I
  132. C
  133. E
  134. R
  135. M
  136. E
  137. D
  138. I
  139. G
  140. I
  141.  
  142. d
  143. o
  144. g
  145. r
  146. u
  147. l
  148. a
  149. n
  150. d
  151. i
  152. .
  153.  
  154. `
  155. s
  156. e
  157. l
  158. e
  159. c
  160. t
  161. R
  162. a
  163. n
  164. d
  165. o
  166. m
  167. C
  168. h
  169. i
  170. l
  171. d
  172. U
  173. r
  174. l
  175. (
  176. )
  177. `
  178. '
  179. i
  180. n
  181.  
  182. `
  183. l
  184. i
  185. n
  186. k
  187. s
  188. `
  189.  
  190. d
  191. i
  192. z
  193. i
  194. s
  195. i
  196. n
  197. e
  198.  
  199. E
  200. K
  201. L
  202. E
  203. M
  204. E
  205.  
  206. Y
  207. A
  208. P
  209. A
  210. R
  211. K
  212. E
  213. N
  214.  
  215. (
  216. '
  217. p
  218. u
  219. s
  220. h
  221. '
  222. )
  223.  
  224. h
  225. e
  226. r
  227. h
  228. a
  229. n
  230. g
  231. i
  232.  
  233. b
  234. i
  235. r
  236.  
  237. E
  238. T
  239. L
  240. D
  241. /
  242. H
  243. O
  244. S
  245. T
  246. N
  247. A
  248. M
  249. E
  250.  
  251. k
  252. a
  253. r
  254. s
  255. i
  256. l
  257. a
  258. s
  259. t
  260. i
  261. r
  262. m
  263. a
  264. s
  265. i
  266.  
  267. (
  268. s
  269. l
  270. i
  271. m
  272. -
  273. l
  274. i
  275. s
  276. t
  277. -
  278. l
  279. a
  280. m
  281. b
  282. d
  283. a
  284. '
  285. n
  286. i
  287. n
  288.  
  289. `
  290. t
  291. l
  292. d
  293. j
  294. s
  295. L
  296. i
  297. b
  298. .
  299. g
  300. e
  301. t
  302. D
  303. o
  304. m
  305. a
  306. i
  307. n
  308. (
  309. )
  310. `
  311. /
  312. `
  313. c
  314. h
  315. i
  316. l
  317. d
  318. L
  319. i
  320. n
  321. k
  322. E
  323. T
  324. l
  325. d
  326.  
  327. !
  328. =
  329. =
  330.  
  331. m
  332. a
  333. i
  334. n
  335. E
  336. T
  337. l
  338. d
  339. `
  340.  
  341. d
  342. e
  343. s
  344. e
  345. n
  346. i
  347. n
  348. i
  349. n
  350.  
  351. B
  352. E
  353. N
  354. Z
  355. E
  356. R
  357. I
  358. N
  359. I
  360. N
  361. )
  362.  
  363. B
  364. U
  365. L
  366. U
  367. N
  368. M
  369. A
  370. D
  371. I
  372. G
  373. I
  374.  
  375. d
  376. o
  377. g
  378. r
  379. u
  380. l
  381. a
  382. n
  383. d
  384. i
  385.  
  386. -
  387. -
  388.  
  389. b
  390. u
  391. ,
  392.  
  393. I
  394. K
  395. I
  396.  
  397. b
  398. e
  399. n
  400. z
  401. e
  402. r
  403.  
  404. a
  405. r
  406. a
  407. c
  408. i
  409. n
  410.  
  411. K
  412. A
  413. R
  414. S
  415. I
  416. L
  417. A
  418. S
  419. T
  420. I
  421. R
  422. M
  423. A
  424. L
  425. I
  426.  
  427. O
  428. K
  429. U
  430. M
  431. A
  432. S
  433. I
  434. Y
  435. L
  436. A
  437.  
  438. t
  439. u
  440. t
  441. a
  442. r
  443. l
  444. i
  445.  
  446. b
  447. i
  448. r
  449.  
  450. S
  451. O
  452. N
  453. U
  454. C
  455. T
  456. U
  457. R
  458.  
  459. (
  460. s
  461. l
  462. i
  463. m
  464. -
  465. l
  466. i
  467. s
  468. t
  469. -
  470. l
  471. a
  472. m
  473. b
  474. d
  475. a
  476.  
  477. A
  478. Y
  479. N
  480. I
  481.  
  482. e
  483. T
  484. L
  485. D
  486. +
  487. 1
  488. -
  489. t
  490. i
  491. p
  492. i
  493.  
  494. f
  495. i
  496. l
  497. t
  498. r
  499. e
  500. l
  501. e
  502. m
  503. e
  504. y
  505. i
  506.  
  507. U
  508. Y
  509. G
  510. U
  511. L
  512. U
  513. Y
  514. O
  515. R
  516. D
  517. U
  518. ,
  519.  
  520. B
  521. U
  522.  
  523. A
  524. R
  525. A
  526. C
  527.  
  528. U
  529. Y
  530. G
  531. U
  532. L
  533. A
  534. M
  535. I
  536. Y
  537. O
  538. R
  539. )
  540. .
  541.  
  542. `
  543. d
  544. o
  545. C
  546. r
  547. a
  548. w
  549. l
  550. (
  551. )
  552. `
  553. '
  554. d
  555. e
  556.  
  557. `
  558. r
  559. a
  560. n
  561. d
  562. o
  563. m
  564. C
  565. h
  566. i
  567. l
  568. d
  569. U
  570. r
  571. l
  572. `
  573. '
  574. i
  575. n
  576.  
  577. `
  578. n
  579. e
  580. w
  581. A
  582. r
  583. g
  584. s
  585. .
  586. u
  587. r
  588. l
  589. `
  590. '
  591. e
  592.  
  593. A
  594. T
  595. A
  596. N
  597. D
  598. I
  599. G
  600. I
  601.  
  602. V
  603. E
  604.  
  605. `
  606. n
  607. e
  608. w
  609. A
  610. r
  611. g
  612. s
  613. `
  614. '
  615. i
  616. n
  617.  
  618. `
  619. p
  620. a
  621. g
  622. e
  623. .
  624. g
  625. o
  626. t
  627. o
  628. (
  629. )
  630. `
  631. '
  632. n
  633. u
  634. n
  635.  
  636. D
  637. O
  638. G
  639. R
  640. U
  641. D
  642. A
  643. N
  644.  
  645. A
  646. R
  647. G
  648. U
  649. M
  650. A
  651. N
  652. I
  653.  
  654. O
  655. L
  656. D
  657. U
  658. G
  659. U
  660.  
  661. (
  662. `
  663. a
  664. s
  665. H
  666. T
  667. T
  668. P
  669. U
  670. r
  671. l
  672. (
  673. a
  674. r
  675. g
  676. s
  677. .
  678. u
  679. r
  680. l
  681. )
  682. `
  683.  
  684. -
  685. >
  686.  
  687. `
  688. u
  689. r
  690. l
  691. T
  692. o
  693. C
  694. r
  695. a
  696. w
  697. l
  698. `
  699.  
  700. -
  701. >
  702.  
  703. `
  704. p
  705. a
  706. g
  707. e
  708. .
  709. g
  710. o
  711. t
  712. o
  713. (
  714. u
  715. r
  716. l
  717. T
  718. o
  719. C
  720. r
  721. a
  722. w
  723. l
  724. ,
  725.  
  726. .
  727. .
  728. .
  729. )
  730. `
  731. )
  732.  
  733. k
  734. o
  735. d
  736. -
  737. A
  738. K
  739. I
  740. S
  741. I
  742.  
  743. t
  744. a
  745. k
  746. i
  747. p
  748.  
  749. e
  750. d
  751. i
  752. l
  753. e
  754. r
  755. e
  756. k
  757.  
  758. d
  759. o
  760. g
  761. r
  762. u
  763. l
  764. a
  765. n
  766. a
  767. b
  768. i
  769. l
  770. i
  771. r
  772. .
  773.  
  774. C
  775. L
  776. I
  777. '
  778. n
  779. i
  780. n
  781.  
  782. y
  783. a
  784. r
  785. d
  786. i
  787. m
  788.  
  789. m
  790. e
  791. t
  792. n
  793. i
  794.  
  795. (
  796. `
  797. p
  798. a
  799. r
  800. s
  801. e
  802. r
  803. .
  804. a
  805. d
  806. d
  807. _
  808. a
  809. r
  810. g
  811. u
  812. m
  813. e
  814. n
  815. t
  816. (
  817. '
  818. -
  819. r
  820. '
  821. ,
  822.  
  823. '
  824. -
  825. -
  826. r
  827. e
  828. c
  829. u
  830. r
  831. s
  832. i
  833. v
  834. e
  835. -
  836. d
  837. e
  838. p
  839. t
  840. h
  841. '
  842. ,
  843.  
  844. {
  845.  
  846. d
  847. e
  848. f
  849. a
  850. u
  851. l
  852. t
  853. :
  854.  
  855. 1
  856. ,
  857.  
  858. h
  859. e
  860. l
  861. p
  862. :
  863.  
  864. '
  865. .
  866. .
  867. .
  868. d
  869. o
  870.  
  871. a
  872. n
  873. o
  874. t
  875. h
  876. e
  877. r
  878.  
  879. c
  880. r
  881. a
  882. w
  883. l
  884.  
  885. t
  886. o
  887.  
  888. t
  889. h
  890. i
  891. s
  892.  
  893. d
  894. e
  895. p
  896. t
  897. h
  898. .
  899.  
  900. D
  901. e
  902. f
  903. a
  904. u
  905. l
  906. t
  907. :
  908.  
  909. 1
  910.  
  911. (
  912. n
  913. o
  914.  
  915. r
  916. e
  917. c
  918. u
  919. r
  920. s
  921. i
  922. o
  923. n
  924. )
  925. .
  926. '
  927.  
  928. }
  929. )
  930. `
  931. )
  932.  
  933. V
  934. A
  935. R
  936. S
  937. A
  938. Y
  939. I
  940. L
  941. A
  942. N
  943.  
  944. D
  945. E
  946. G
  947. E
  948. R
  949. I
  950.  
  951. A
  952. C
  953. I
  954. K
  955. C
  956. A
  957.  
  958. B
  959. E
  960. L
  961. G
  962. E
  963. L
  964. I
  965. Y
  966. O
  967. R
  968.  
  969. -
  970. -
  971.  
  972. b
  973. u
  974. ,
  975.  
  976. b
  977. i
  978. r
  979.  
  980. c
  981. a
  982. l
  983. i
  984. s
  985. t
  986. i
  987. r
  988. m
  989. a
  990.  
  991. G
  992. E
  993. R
  994. E
  995. K
  996. T
  997. I
  998. R
  999. M
  1000. E
  1001. Y
  1002. E
  1003. N
  1004. ,
  1005.  
  1006. A
  1007. R
  1008. A
  1009. C
  1010. I
  1011. N
  1012.  
  1013. K
  1014. E
  1015. N
  1016. D
  1017. I
  1018.  
  1019. K
  1020. A
  1021. Y
  1022. N
  1023. A
  1024. K
  1025. -
  1026. K
  1027. O
  1028. D
  1029. U
  1030.  
  1031. S
  1032. A
  1033. T
  1034. I
  1035. R
  1036. I
  1037. N
  1038. D
  1039. A
  1040.  
  1041. O
  1042. K
  1043. U
  1044. N
  1045. A
  1046. B
  1047. I
  1048. L
  1049. E
  1050. N
  1051.  
  1052. b
  1053. i
  1054. r
  1055.  
  1056. G
  1057. E
  1058. R
  1059. C
  1060. E
  1061. K
  1062. .

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
In `src/brave/page.ts::selectRandomChildUrl()`, every `<a href>` link on a crawled page is collected (validated only by `checks.ts::asHTTPUrl()`, which checks solely that the URL's protocol starts with `http` -- no hostname or IP-range restriction, no same-origin/same-eTLD+1 restriction of any kind), and one is chosen at random to become the next recursive crawl target. In `src/brave/crawl.ts::doCrawl()`, when `args.recursiveDepth > 1` (an explicit opt-in CLI flag, `-r`/`--recursive-depth`, default `1` meaning no recursion, per the tool's own help text: "choose a link at random on page and do another crawl to this depth"), this randomly-selected link becomes the `url` argument of a new top-level `doCrawl()` invocation, which is then passed directly to `page.goto(urlToCrawl, { waitUntil: 'domcontentloaded' })` -- a full page navigation, not merely a subresource load. This means that, when the tool is run with recursion enabled (a documented, intended feature for broader site exploration, consistent with the tool's stated purpose of gathering pagegraph data "from all over the internet" at scale), any page encountered during the crawl -- the initial target or any page reached during the random walk -- can embed a link to an internal address (e.g. `http://169.254.169.254/...`, `http://localhost:<port>/...`, or any other address reachable from the crawling machine's network position) and the tool will fully navigate to and render it. Where `--screenshot` and/or `--store-har`/`--store-har-body` are enabled (also documented CLI options), the tool will capture and persist to disk a screenshot of that internal page and/or the full HTTP request/response bodies observed while loading it -- not merely a hash or status code, but the actual response content. This SSRF risk is more direct than a comparable issue already reported this session in `brave/slim-list-lambda` (which restricted recursive navigation to the same eTLD+1 and only recorded a SHA-256 hash of response bodies, not their content); this tool applies no domain restriction at all to its recursive navigation target and can capture full response content. The practical likelihood depends on how this tool is actually invoked in Brave's research/production pipelines (what `--recursive-depth` value is used, and what network/infrastructure context it runs in), which could not be confirmed from the source code alone. Suggested fix: when selecting a child URL to recursively navigate to, reject links whose resolved hostname is a private/loopback/link-local IP address or the cloud metadata address (and consider also restricting to the same eTLD+1 as the page being crawled, matching the defense already applied in `brave/slim-list-lambda`), in addition to the existing protocol check.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._