# Bug Bounty Raporu — brave_adblock-lists-mirror

**Tarih:** 2026-11-04 03:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/adblock-lists-mirror (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Python. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_adblock-lists-mirror/raw`
* **Engellenen/erişilemeyen adımlar:** update-lists.py'nin cektigi gercek `list_catalog.json` (https://raw.githubusercontent.com/brave/adblock-resources/master/filter_lists/list_catalog.json) icerigi -- yani TOPLANAN onlarca ucuncu-taraf filtre-listesinin TAM listesi ve her birinin editoryal/bakim surecinin ne kadar sIkI oldugu -- bu teslimde yok. Bu nedenle F1'in 'bu listelerden en az biri attacker-kontrol edilebilir mi' sorusu, somut liste-bazinda DOGRULANAMADI; bulgu, delivered kodun KENDI yapisal zafiyetine (escape eksikligi) dayaniyor., site/search.js'in gercekte HANGI sayfada/domainde, HANGI CSP (Content-Security-Policy) basligi ile servis edildigi bu teslimde yok (index.html veya hosting config dosyasi gelmedi) -- bu nedenle bir CSP'nin bu XSS'i KISMEN azaltip-azaltmadigi (orn. inline event-handler'lari bloke eden strict bir CSP) dogrulanamadi; asagidaki bulgu, kod-seviyesindeki escape-eksikligi gercegine dayanıyor, varsayilan/CSP'siz bir servis senaryosunu temel aliyor.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, beklenenin disinda: 'adblock-lists-mirror', Brave tarayicisina gonderilen reklam-engelleme filtre listelerini ARSIVLEYEN/ayna goruntuleyen KUCUK bir Python+JS repo'su -- C++ tarayici motoru DEGIL. Teslim edilen TUM dosyalar (README, create_db.py, search.js, update-lists.py + iki commit diff'i) OKUNDU.
* Iki commit diff'i (7f0810d3c7, fe86bbdb22) incelendi: ikisi de salt BAGIMLILIK-GUNCELLEME commit'leri (npm package-lock.json guvenlik-yama guncellemeleri: serialize-javascript, shell-quote, qs, proxy-addr vb.; aiohttp 3.14.3 -> 3.14.4) -- GUVENLIK ACISINDAN IYILESTIRME niteliginde, kendi basina bir REGRESYON/bulgu DEGIL.
* update-lists.py ozellikle dikkatle incelendi: indirme boyutu 100MB ile sinirlandirilmis (DoS/disk-doldurma onlemi), checksum dogrulamasi (EasyList disindaki kaynaklar icin) var, dosya adlari URL'nin MD5 hash'inden turetiliyor (path-traversal riski YOK -- hash HER ZAMAN sabit-uzunlukta hex). Bu dosyada F1 disinda baska bir bulgu tespit edilmedi.
* create_db.py incelendiginde, SQL enjeksiyonu riski YOK (TUM INSERT'ler parametrize `?` placeholder'lari kullaniyor, string-format/concat YOK) -- sadece CIKIS-KODLAMASI (output encoding) katmaninda (search.js) bir eksiklik var, VERITABANI KATMANINDA degil.
* SONUC: Bu kucuk repo'da, zincirin SADECE SON halkasinda (search.js'in innerHTML kullanimi) ama NET ve dogrulanabilir bir DOM-tabanli XSS bulgusu (F1) tespit edildi -- kod-seviyesinde KESIN (escape yok), gercek-dunya-sömürülebilirligi ise aggregat edilen ucuncu-taraf filtre-listelerinden en az birinin icerigine bagli (bu teslimde tam olarak sayilamadi).

## 📊 Bulgu F1: site/search.js: arama sonucu olarak gosterilen `rule` metni (mirror edilen UCUNCU-TARAF adblock filtre listelerinden DOGRUDAN, HICBIR HTML-escaping YAPILMADAN alinan ham satir icerigi) `.innerHTML` uzerinden DOM'a yaziliyor -- DOM-tabanli XSS
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** medium-high (gercek kod-seviyesi XSS sink'i; attacker-erisilebilirligi, aggregat edilen ONLARCA ucuncu-taraf filtre-listesinden EN AZ BIRININ bir satirinin manipule edilebilmesine bagli)
* **Zafiyet Sınıfı (CWE):** CWE-79 (Improper Neutralization of Input During Web Page Generation / Cross-site Scripting)
* **Stage 2 Confidence:** 55/100 — Kod-seviyesi iddiayi curutmeye calistim ve BASARISIZ oldum: search.js'in TAMAMI satir-satir yeniden okundu, `rule`/`source_file` degerlerinin `item.innerHTML = \`...${rule}...\`` icinde HICBIR escape/textContent kullanilmadan interpole edildigi KESIN -- bu, DOM/JS'in kendi semantigiyle (innerHTML atamasi HTML-parse eder) dogrulanan, tartismasiz bir statik gercek. create_db.py'nin karsilastirmali okumasi da dogrulandi: `rule_text.lower()` DISINDA HICBIR sanitizasyon yok. Bunu REJECT etmeye calisirken denedigim itirazlar: (1) 'Belki CSP bunu engeller' -- ama bu teslimde index.html/CSP konfigurasyonu YOK, bu nedenle VARSAYILAN/savunmasiz senaryoyu temel almak gerekiyor (ayrica DOM XSS'in innerHTML-tabanli bir varyanti, img-onerror gibi inline event-handler'lar HTTP-only bir strict-dynamic CSP'de bile bazi durumlarda calisabilir -- kesin degil ama varsayilan guvensiz kabul etmek dogru). (2) 'Attacker filtre-listesine satir eklemesi gerceklesebilir mi' -- bu TEK gercek belirsizlik: tam liste-katalogu (list_catalog.json) bu teslimde yok, dolayisiyla KAC listenin/ne kadar siki editoryal surecin oldugu bilinmiyor. ANCAK bilinen kamuya acik gercek: brave/adblock-resources'in katalogu GERCEKTEN onlarca BAGIMSIZ ucuncu-taraf/bolgesel/toplum-bakimli listeyi (EasyList'in kendisinin YANI SIRA cok sayida kucuk-olcekli, daha az siki denetimli bolgesel/dil-bazli liste) icerir -- bu, program-disi bir web-arama ile dogrulanabilecek, genel bilgi niteliginde bir gercek, OYSA ben BURADA sadece delivered kod uzerinden statik muhakeme yapiyorum, bu varsayimi KANIT olarak KULLANMIYORUM, sadece confidence'i ORTA-YUKSEK (tam-kesin degil) tutmak icin bir faktor olarak not ediyorum. (3) 'Bu bir self-inflicted/ayni-taraf sorunu mu' -- HAYIR: filtre-listesinin bakimcisi/kaynagi ile arama sitesinin ZIYARETCISI AYRI taraflar; Brave'in KENDI islettigi arama aracinin KULLANICILARI, ucuncu-taraf liste-icerigi araciligiyla etkileniyor -- bu, `base_onchainsummer.xyz` PASS kararindaki 'gercek ucuncu-taraf kaynak-suistimali' kalibrasyon eksenine BENZER (confidence 55), ORADA oldugu gibi BURADA da 'bu sitenin KENDI operasyonel sinirini asan bir ucuncu-taraf etkisi' var. PASS confidence'i 65'e DEGIL 55'e sabitliyorum CUNKU somut bir 'bu listede gercekten boyle bir satir var/olusturulabilir' KANITI (orn. mevcut bir filtre listesinde fiilen HTML-benzeri bir satir) GOSTERILEMEDI -- sadece YAPISAL (kod-seviyesi escape-eksikligi + genis-govdeli ucuncu-taraf veri-kaynagi) bir zafiyet DOGRULANDI, fiili-sömürü KANITLANAMADI.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** site/search.js, search() fonksiyonu icindeki sonuc-render dongusu (`for (const row of rows) { ... item.innerHTML = ... }`); kaynak veri create_db.py'nin `rules_content.rule` sutunundan geliyor
* **Kanıt kaynağı:** `site/search.js`
* **Kanıt alıntısı:**
  ```
  const rule = row[0];
const source_file = row[1];
const line_number = row[2];

const githubUrl = `https://github.com/brave/adblock-lists-mirror/blob/lists/lists/${source_file}#L${line_number}`;

item.innerHTML = `
    <pre>${rule}</pre>
    <a href="${githubUrl}" target="_blank">
        ${source_file} (line ${line_number})
    </a>
`;
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** Zincirin UCU BURADA: `rule` degiskeni, SQLite FTS5 tablosundan ('rules' tablosu, arama sorgusunun MATCH ettigi satir) DOGRUDAN okunuyor ve `item.innerHTML = ...` ile bir template literal icinde HICBIR escaping/sanitizasyon (orn. `textContent` kullanimi, `DOMPurify`, veya manuel `&lt;`/`&gt;` donusumu) YAPILMADAN DOM'a yaziliyor. Eger `rule` metni `<img src=x onerror=alert(document.domain)>` veya `</pre><script>...</script>` gibi HTML/JS iceren bir dizi ise, tarayici bunu METIN olarak DEGIL, calistirilacak MARKUP olarak yorumlar -- klasik DOM-tabanli XSS. BU METNIN KAYNAGI ise zincirin diger ucunda: `update-lists.py`, `list_catalog.json`'da (brave/adblock-resources deposundan) tanimli ONLARCA farkli ucuncu-taraf URL'den (EasyList'in kendisi disinda, muhtemelen cok sayida bagimsiz/bolgesel/toplum-bakimli filtre listesi -- bu teslimde liste TAM OLARAK sayilamadi, bkz. blocked_or_unreachable_steps) ham metin dosyalari indiriyor; `create_db.py` bu dosyalardaki HER satiri (`!` ile baslayan yorumlar ve `data:` satirlari HARIC) TEK kontrolu 'bos mu' olan bir filtreyle, SADECE kucuk harfe cevirerek (`rule_text.lower()`), HICBIR HTML-guvenligi / karakter-dogrulamasi YAPMADAN veritabanina yaziyor. Yani zincirde HICBIR ASAMADA (indirme -> veritabani-yazma -> arama-sonucu-render) `rule` metninin HTML-metakarakterleri icerip-icermedigi KONTROL EDILMIYOR -- sadece son adimda (`search.js`) bu, DOGRUDAN bir XSS sink'ine (`innerHTML`) besleniyor. Saldirgan modeli: aggregat edilen onlarca ucuncu-taraf filtre-listesinden EN AZ BIRINE (orn. daha az siki editoryal denetimli bir bolgesel/toplum listesine) kontrollu bir satir eklemeyi basarabilen biri (liste bakimcisinin kendisi, ele gecirilmis bir liste-kaynagi, veya zayif PR-inceleme sureci olan bir topluluk listesine katkida bulunan biri), bu sitenin arama sonuclarini goruntuleyen HERHANGI bir ziyaretcide (arama terimi o satiri eslestirdiginde) JavaScript calistirabilir -- bu, filtre-listesinin KENDI SAHIBI/bakim surecinin disindaki, Brave'in KENDI ISLETTIGI arama sitesinin KULLANICILARINI etkileyen bir zincir, dolayisiyla saf 'ayni-taraf-kendi-kendine-zarar' degil.
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
  32. g
  33. e
  34. r
  35. e
  36. k
  37. t
  38. i
  39. r
  40. m
  41. e
  42. z
  43. )
  44. :
  45.  
  46. s
  47. e
  48. a
  49. r
  50. c
  51. h
  52. .
  53. j
  54. s
  55. '
  56. d
  57. e
  58.  
  59. `
  60. r
  61. u
  62. l
  63. e
  64. `
  65. /
  66. `
  67. s
  68. o
  69. u
  70. r
  71. c
  72. e
  73. _
  74. f
  75. i
  76. l
  77. e
  78. `
  79.  
  80. d
  81. e
  82. g
  83. i
  84. s
  85. k
  86. e
  87. n
  88. l
  89. e
  90. r
  91. i
  92. n
  93. i
  94. n
  95.  
  96. `
  97. i
  98. t
  99. e
  100. m
  101. .
  102. i
  103. n
  104. n
  105. e
  106. r
  107. H
  108. T
  109. M
  110. L
  111.  
  112. =
  113.  
  114. \
  115. `
  116. .
  117. .
  118. .
  119. $
  120. {
  121. r
  122. u
  123. l
  124. e
  125. }
  126. .
  127. .
  128. .
  129. \
  130. `
  131. `
  132.  
  133. t
  134. e
  135. m
  136. p
  137. l
  138. a
  139. t
  140. e
  141.  
  142. l
  143. i
  144. t
  145. e
  146. r
  147. a
  148. l
  149. '
  150. i
  151.  
  152. i
  153. c
  154. i
  155. n
  156. d
  157. e
  158.  
  159. D
  160. O
  161. G
  162. R
  163. U
  164. D
  165. A
  166. N
  167.  
  168. i
  169. n
  170. t
  171. e
  172. r
  173. p
  174. o
  175. l
  176. e
  177.  
  178. e
  179. d
  180. i
  181. l
  182. d
  183. i
  184. g
  185. i
  186. ,
  187.  
  188. a
  189. y
  190. n
  191. i
  192.  
  193. d
  194. o
  195. s
  196. y
  197. a
  198. d
  199. a
  200.  
  201. b
  202. a
  203. s
  204. k
  205. a
  206.  
  207. H
  208. E
  209. R
  210. H
  211. A
  212. N
  213. G
  214. I
  215.  
  216. b
  217. i
  218. r
  219.  
  220. y
  221. e
  222. r
  223. d
  224. e
  225.  
  226. `
  227. e
  228. s
  229. c
  230. a
  231. p
  232. e
  233. H
  234. t
  235. m
  236. l
  237. `
  238. /
  239. `
  240. t
  241. e
  242. x
  243. t
  244. C
  245. o
  246. n
  247. t
  248. e
  249. n
  250. t
  251. `
  252. /
  253. D
  254. O
  255. M
  256. P
  257. u
  258. r
  259. i
  260. f
  261. y
  262.  
  263. g
  264. i
  265. b
  266. i
  267.  
  268. b
  269. i
  270. r
  271.  
  272. s
  273. a
  274. n
  275. i
  276. t
  277. i
  278. z
  279. a
  280. s
  281. y
  282. o
  283. n
  284.  
  285. y
  286. a
  287. r
  288. d
  289. i
  290. m
  291. c
  292. i
  293. s
  294. i
  295. n
  296. i
  297. n
  298.  
  299. T
  300. A
  301. N
  302. I
  303. M
  304. L
  305. A
  306. N
  307. M
  308. A
  309. D
  310. I
  311. G
  312. I
  313.  
  314. v
  315. e
  316. y
  317. a
  318.  
  319. c
  320. a
  321. g
  322. i
  323. r
  324. i
  325. l
  326. m
  327. a
  328. d
  329. i
  330. g
  331. i
  332.  
  333. d
  334. o
  335. g
  336. r
  337. u
  338. l
  339. a
  340. n
  341. a
  342. b
  343. i
  344. l
  345. i
  346. r
  347.  
  348. (
  349. d
  350. o
  351. s
  352. y
  353. a
  354. n
  355. i
  356. n
  357.  
  358. T
  359. A
  360. M
  361. A
  362. M
  363. I
  364. ,
  365.  
  366. ~
  367. 1
  368. 4
  369. 7
  370.  
  371. s
  372. a
  373. t
  374. i
  375. r
  376. ,
  377.  
  378. s
  379. a
  380. t
  381. i
  382. r
  383. -
  384. s
  385. a
  386. t
  387. i
  388. r
  389.  
  390. o
  391. k
  392. u
  393. n
  394. d
  395. u
  396. )
  397. .
  398.  
  399. c
  400. r
  401. e
  402. a
  403. t
  404. e
  405. _
  406. d
  407. b
  408. .
  409. p
  410. y
  411. '
  412. n
  413. i
  414. n
  415.  
  416. k
  417. a
  418. r
  419. s
  420. i
  421. l
  422. a
  423. s
  424. t
  425. i
  426. r
  427. m
  428. a
  429. l
  430. i
  431.  
  432. o
  433. k
  434. u
  435. m
  436. a
  437. s
  438. i
  439. :
  440.  
  441. `
  442. r
  443. u
  444. l
  445. e
  446. s
  447. _
  448. c
  449. o
  450. n
  451. t
  452. e
  453. n
  454. t
  455. `
  456.  
  457. t
  458. a
  459. b
  460. l
  461. o
  462. s
  463. u
  464. n
  465. a
  466.  
  467. I
  468. N
  469. S
  470. E
  471. R
  472. T
  473.  
  474. e
  475. d
  476. i
  477. l
  478. e
  479. n
  480.  
  481. `
  482. r
  483. u
  484. l
  485. e
  486. _
  487. t
  488. e
  489. x
  490. t
  491. `
  492. '
  493. i
  494. n
  495.  
  496. S
  497. A
  498. D
  499. E
  500. C
  501. E
  502.  
  503. `
  504. .
  505. l
  506. o
  507. w
  508. e
  509. r
  510. (
  511. )
  512. `
  513.  
  514. d
  515. o
  516. n
  517. u
  518. s
  519. u
  520. m
  521. u
  522. n
  523. e
  524.  
  525. u
  526. g
  527. r
  528. a
  529. d
  530. i
  531. g
  532. i
  533. ,
  534.  
  535. H
  536. I
  537. C
  538. B
  539. I
  540. R
  541.  
  542. e
  543. s
  544. c
  545. a
  546. p
  547. e
  548. /
  549. s
  550. t
  551. r
  552. i
  553. p
  554.  
  555. i
  556. s
  557. l
  558. e
  559. m
  560. i
  561. n
  562. e
  563.  
  564. U
  565. G
  566. R
  567. A
  568. M
  569. A
  570. D
  571. I
  572. G
  573. I
  574.  
  575. d
  576. o
  577. g
  578. r
  579. u
  580. l
  581. a
  582. n
  583. a
  584. b
  585. i
  586. l
  587. i
  588. r
  589. .
  590.  
  591. B
  592. u
  593. ,
  594.  
  595. J
  596. a
  597. v
  598. a
  599. S
  600. c
  601. r
  602. i
  603. p
  604. t
  605. /
  606. D
  607. O
  608. M
  609. '
  610. u
  611. n
  612.  
  613. k
  614. e
  615. n
  616. d
  617. i
  618.  
  619. s
  620. e
  621. m
  622. a
  623. n
  624. t
  625. i
  626. g
  627. i
  628. y
  629. l
  630. e
  631.  
  632. (
  633. b
  634. i
  635. r
  636.  
  637. e
  638. l
  639. e
  640. m
  641. e
  642. n
  643. t
  644. i
  645. n
  646.  
  647. `
  648. .
  649. i
  650. n
  651. n
  652. e
  653. r
  654. H
  655. T
  656. M
  657. L
  658. `
  659. '
  660. i
  661. n
  662. e
  663.  
  664. a
  665. t
  666. a
  667. n
  668. a
  669. n
  670.  
  671. m
  672. e
  673. t
  674. i
  675. n
  676.  
  677. H
  678. T
  679. M
  680. L
  681.  
  682. o
  683. l
  684. a
  685. r
  686. a
  687. k
  688.  
  689. P
  690. A
  691. R
  692. S
  693. E
  694.  
  695. E
  696. D
  697. I
  698. L
  699. I
  700. R
  701. ,
  702.  
  703. `
  704. .
  705. t
  706. e
  707. x
  708. t
  709. C
  710. o
  711. n
  712. t
  713. e
  714. n
  715. t
  716. `
  717. '
  718. i
  719. n
  720.  
  721. a
  722. k
  723. s
  724. i
  725. n
  726. e
  727. )
  728.  
  729. d
  730. o
  731. g
  732. r
  733. u
  734. l
  735. a
  736. n
  737. a
  738. n
  739. ,
  740.  
  741. c
  742. a
  743. l
  744. i
  745. s
  746. t
  747. i
  748. r
  749. m
  750. a
  751.  
  752. G
  753. E
  754. R
  755. E
  756. K
  757. T
  758. I
  759. R
  760. M
  761. E
  762. Y
  763. E
  764. N
  765.  
  766. b
  767. i
  768. r
  769.  
  770. s
  771. t
  772. a
  773. t
  774. i
  775. k
  776.  
  777. g
  778. e
  779. r
  780. c
  781. e
  782. k
  783. .

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
In `site/search.js`, the client-side search page for this repository's mirrored adblock filter lists renders each FTS5 search-result row via `item.innerHTML = \`<pre>${rule}</pre><a href="${githubUrl}">...\`` -- directly interpolating `rule` (the raw matched line of filter-list text, column `rules_content.rule`) into HTML with no escaping of any kind. The upstream pipeline provides no sanitization either: `update-lists.py` downloads filter-list files from dozens of third-party URLs listed in `brave/adblock-resources`'s `list_catalog.json`, and `create_db.py` imports every non-comment, non-empty line verbatim into the searchable database (lowercasing only -- no HTML-safety validation). The net effect is a DOM-based XSS: a line such as `<img src=x onerror=alert(document.domain)>` (or any other filter-list line containing HTML/script markup) present in ANY of the aggregated third-party filter lists would be stored as-is and, when a visitor's search query matches that row, rendered as live markup in the visitor's browser on this site's origin -- rather than as the literal filter-rule text a `<pre>` block implies. This is a classic missing-output-encoding defect (the fix is a one-line change: use `textContent`/`createTextNode` or an HTML-escaping helper instead of raw `innerHTML` interpolation for `rule` and `source_file`), but its practical trigger depends on whether at least one of the many third-party filter lists aggregated by this mirror can have such a line introduced into it (by a list's own maintainer, a compromised upstream source, or a less-rigorously-reviewed community/regional list) -- this repository's own code provides no defense-in-depth against that regardless of how well-curated any individual upstream list is believed to be. Suggested fix: HTML-escape (or use `textContent`) for all filter-list-derived and filename-derived values before inserting them into the DOM in `search.js`, and/or reject or HTML-escape lines containing `<`/`>`/`"` at ingestion time in `create_db.py` as defense-in-depth.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._