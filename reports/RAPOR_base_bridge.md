# Bug Bounty Raporu — base_bridge

**Tarih:** 2026-11-03 12:44 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase / Base (https://hackerone.com/coinbase) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: https://github.com/base/* -> https://github.com/base/bridge (structured_scope id: 1028889, eligible_for_bounty: true, max_severity: critical). Language: TypeScript. Description: Production repository.
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_bridge/raw`
* **Engellenen/erişilemeyen adımlar:** Solana (Rust) tarafindaki program kodu teslim edilmedi -- yalnizca Base-tarafi Solidity sozlesmeleri + Solana programina karsi uretilen TypeScript istemci kodu (clients/ts/.../generated/*) teslim edildi. Bu nedenle F1'in Solana-tarafi karsiligi (registerRemoteToken mesajinin Solana programi tarafindan NASIL/NE ZAMAN gonderildigi, tekrar-gonderime karsi Solana-tarafi bir koruma olup olmadigi) DOGRULANAMADI -- F1, Base-tarafi sozlesme kodunun KENDI ICINDE hic bir ek koruma (idempotency guard) icermedigi gercegine dayaniyor, bu kisim tam olarak dogrulanabilir ve Solana tarafindan BAGIMSIZ bir zayifliktir.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Base'in Solana<->Base koprusu (base/bridge) -- YUKSEK DEGERLI, dogrudan fon ozelligine sahip bir hedef. Son iki commit SADECE README/SECURITY.md dokumantasyon eklemeleri -- kod etkisi yok. ONEMLI NOT: Eklenen SECURITY.md'ye gore, bu depodaki 'deployed smart contracts' (orn. Bridge.sol, TokenLib.sol) resmi olarak CANTINA bug-bounty programi kapsaminda ('5 million-dollar Cantina bug bounty program... to cover all deployed smart contracts for Base'), HackerOne'in kapsami ise 'offchain components and services' olarak belirtiliyor. Bu nedenle F1 (bir deployed smart contract'taki bulgu) teknik olarak HackerOne'in structured_scope wildcard'inda (github.com/base/*) gorunse de, operator F1'i RAPORLARKEN muhtemelen CANTINA platformunu tercih etmeli -- bu rapor yine de standart pipeline akisina (RAPOR_<hedef>.md + ipucu/Telegram) gore uretiliyor, ancak gonderim platformu secimi icin bu notu dikkate alin.
* Bridge.sol'daki mesaj-tekrar-calistirma korumasi (`successes[messageHash]`), BridgeValidator'daki multisig esik dogrulamasi (sirali-imzalayan + yinelenen-imzalayan koruma, dogru uygulanmis), VerificationLib'in guvenli baslangic durumu (threshold=type(uint128).max initialize'dan once), ve CrossChainERC20'nin mint/burn erisim kontrolu (onlyBridge, dogru uygulanmis) AYRINTILI incelendi -- F1 DISINDA bir sorun bulunamadi bu alanlarda.
* CrossChainERC20Factory.deploy() izinsiz (permissionless) ama guvenli -- deterministik CREATE2 adresi (remoteToken,name,symbol,decimals) tam tuple'ina bagli, farkli parametrelerle deploy edilen bir token FARKLI bir adrese sahip olur ve Bridge/TokenLib yalnizca mesaj icinde ACIKCA belirtilen `localToken` adresine guvenir -- izinsiz deploy kendi basina bir saldiri yuzeyi acmiyor.
* MessageStorageLib.sol'daki MMR (Merkle Mountain Range) implementasyonu (giden/Base->Solana mesaj kanitlama) karmasik ama zaman kisitlamasi nedeniyle YALNIZCA yuzeysel incelendi -- bu, ciddi bir ikinci-geçiş inceleme konusu olabilir, ancak F1'in ciddiyeti ve zaten dogrulanmis olmasi nedeniyle bu oturumda derinlemesine dogrulanmadi (blocked_or_unreachable_steps'e not edildi).
* Solana (Rust) program kodu bu teslimatta YOKTU -- F1'in Base-tarafi bulgusu, Solana tarafindan BAGIMSIZ, tek basina gecerlidir (Base sozlesmesinin kendi ic mantiginda bir idempotency eksikligi).

## 📊 Bulgu F1: TokenLib.registerRemoteToken(): scalar yeniden-kayit korumasi yok -- tek bir (oracle onayli) mesaj, bir token ciftinin TUM tarihsel depozito havuzunu bosaltabilir
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** critical
* **Zafiyet Sınıfı (CWE):** CWE-841 (Improper Enforcement of Behavioral Workflow) / is-mantigi erisim kontrolu eksikligi -- kritik fon-guvenligi etkisi
* **Stage 2 Confidence:** 65/100 — F1'i curutmeye calisirken onemli bir nuance ortaya cikti, bunu seffaf sekilde not ediyorum: `registerRemoteToken` VE `finalizeTransfer`'in KENDISI (hatta scalar manipulasyonu OLMADAN) AYNI oracle/validator esigini (BridgeValidator.validMessages) gectirmeyi gerektiriyor -- yani bir saldirganin DOGRUDAN, buyuk bir `remoteAmount` (uint64 max ~1.8e19) tasiyan TEK bir `finalizeTransfer` mesaji forge etmesi de, EGER o cift icin scalar zaten '1e12' gibi makul-gorunen bir deger ise, teorik olarak ZATEN devasa bir localAmount (1.8e19 * 1e12) uretebilir -- bu, HER oracle-tabanli (Stage 0) kopru icin KABUL EDILMIS, dokumante edilmis temel guven modelidir (oracle compromise = kopru compromise). Bu nedenle F1'in katkisi, saldirganin 'oracle esigini gecme' zorlugunu DEGISTIRMIYOR (ayni esik her iki yolda da gerekli) -- bunun yerine IKI farkli ONEMLI deger katiyor: (1) SESSIZLIK/TESPIT-EDILEBILIRLIK: tek, acikca anormal buyuk remoteAmount'lu bir mesaj validator'lar/izleme sistemleri tarafindan supheli gorunebilir; iki ayri, her biri 'normal gorunen' mesaj (hafif yuksek bir scalarExponent + sonrasinda KUCUK gorunen bir remoteAmount) cok daha az dikkat cekici bir saldiri yuzeyi sunar. (2) EN ONEMLISI -- scalar bozulmasi SADECE KOTU NIYETE bagli DEGIL: Solana-tarafi relayer/programinda ONDALIK-DONUSUMU ile ilgili SAF, kasitsiz bir HATA (malis olmadan, dürüst validatorlar tarafindan imzalanan) KALICI OLARAK devreye girip, sonraki TUM (dürüst kullanicilarin dahi gonderdigi) kucuk cekim mesajlarinin devasa miktarlar hesaplamasina yol acabilir -- bu, 'bir mesaj = bir hata' baseline riskinden NITELIKSEL olarak farkli ve DAHA KOTU bir failure mode (kalici state bozulmasi + TUM gelecekteki islemler icin genis blast radius). Bu nedenle F1'i GECERLI, ANLAMLI bir defense-in-depth/is-mantigi bulgusu olarak PASS yapiyorum -- ancak 'zaten var olan oracle-guven-modelinden BAGIMSIZ olarak yeni bir saldiri YUZEYI aciyor' seklinde ASIRI iddiali bir cerceveden ziyade, 'blast-radius buyutme + durust-hata-karsi-savunmasizlik' cercevesiyle. Onerilen duzeltme (registerRemoteToken'da tek-seferlik/idempotency kontrolu) ucuz, basit, ve riski onemli olcude azaltir -- bu tur 'dusuk-maliyetli, yuksek-degerli savunma katmani eksikligi' bulgulari bagimsiz guvenlik denetimlerinde (Cantina dahil) duzenli olarak orta-yuksek siddette raporlanir.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** base/src/libraries/TokenLib.sol, fonksiyon registerRemoteToken() (satir ~3040); etkilenen cagiran: Bridge.sol::__relayMessage() (REMOTE_BRIDGE mesaj dalinda)
* **Kanıt kaynağı:** `base/src/libraries/TokenLib.sol`
* **Kanıt alıntısı:**
  ```
  function registerRemoteToken(address localToken, Pubkey remoteToken, uint8 scalarExponent) internal {
    TokenLibStorage storage $ = getTokenLibStorage();
    $.scalars[localToken][remoteToken] = 10 ** scalarExponent;
}
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** `TokenLib.registerRemoteToken()` `$.scalars[localToken][remoteToken]` degerini KOSULSUZ olarak uzerine yaziyor -- onceden bir scalar ayarlanmis olsa bile (`require($.scalars[...] == 0, ...)` gibi bir idempotency/tek-seferlik koruma YOK). Bu fonksiyon, `Bridge.__relayMessage()` icinde `message.sender == REMOTE_BRIDGE` oldugunda cagriliyor -- yani Solana bridge programinin KENDISININ gonderdigi, `BridgeValidator.validMessages()` (oracle/validator multisig) tarafindan onaylanmasi gereken bir mesaj turu.

Kritik olan: `TokenLib.finalizeTransfer()` (ETH ve native-ERC20 'geri-cekme' yollari) `localAmount = transfer.remoteAmount * scalar` hesaplar ve ardindan `$.deposits[localToken][remoteToken] -= localAmount` ile TARIHSEL-TOPLAM depozito defterinden dusurur (yetersizse Solidity 0.8'in otomatik underflow-revert'i korur). `deposits`, GECMISTE o cift icin BIRIKMIS TUM yerel tutari (hangi scalar ile yatirilmis olursa olsun) tutuyor -- scalar DEGISTIGINDE bu birikmis havuz YENIDEN HESAPLANMIYOR.

Sonuc: Eger (herhangi bir nedenle -- kotu niyetli validator coalition, tek bir ele gecirilmis/zorlanan validator seti, VEYA Solana-tarafi relayer/program kodunda saf bir HATA, orn. ayni token kaydini yanlislikla FARKLI bir ondalik-ustel ile tekrar gondermek) scalarExponent'i NORMALDEN cok daha buyuk bir deger ile tasiyan IKINCI bir `registerRemoteToken` mesaji bir kez dahi oracle tarafindan onaylanirsa, scalar KALICI olarak degisir. Bu noktadan sonra TEK BIR, KUCUK GORUNEN bir `finalizeTransfer` mesaji (orn. remoteAmount=1) `localAmount = 1 * yeniScalar` hesaplar ve eger bu deger `deposits[...]`'e esit veya daha azsa, O TOKEN CIFTI ICIN TARIHSEL OLARAK YATIRILMIS TUM FONLARI TEK SEFERDE BOSALTABILIR -- orijinal kotu-niyetli/hatali mesajin kendi tasidigi deger ile SINIRLI DEGIL, cift icin bridge'e kilitlenmis TUM kullanicilarin fonlarini etkiler.

`scalarExponent` bir `uint8` (0-255) oldugundan ve Solidity 0.8'in `**` operatoru overflow-korumali oldugundan, deger ~10^77'ye kadar cikabilir (ornegin 10^40 bile, gercekci hicbir token decimal farki icin gerekli olmayan, havuzu kolayca drene edecek bir deger olurdu).
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
  22. r
  23. e
  24. g
  25. i
  26. s
  27. t
  28. e
  29. r
  30. R
  31. e
  32. m
  33. o
  34. t
  35. e
  36. T
  37. o
  38. k
  39. e
  40. n
  41. (
  42. )
  43. `
  44.  
  45. f
  46. o
  47. n
  48. k
  49. s
  50. i
  51. y
  52. o
  53. n
  54. u
  55. n
  56. d
  57. a
  58.  
  59. `
  60. $
  61. .
  62. s
  63. c
  64. a
  65. l
  66. a
  67. r
  68. s
  69. [
  70. l
  71. o
  72. c
  73. a
  74. l
  75. T
  76. o
  77. k
  78. e
  79. n
  80. ]
  81. [
  82. r
  83. e
  84. m
  85. o
  86. t
  87. e
  88. T
  89. o
  90. k
  91. e
  92. n
  93. ]
  94. `
  95.  
  96. a
  97. t
  98. a
  99. m
  100. a
  101. s
  102. i
  103. n
  104. d
  105. a
  106. n
  107.  
  108. O
  109. N
  110. C
  111. E
  112.  
  113. h
  114. i
  115. c
  116.  
  117. b
  118. i
  119. r
  120.  
  121. `
  122. r
  123. e
  124. q
  125. u
  126. i
  127. r
  128. e
  129. (
  130. $
  131. .
  132. s
  133. c
  134. a
  135. l
  136. a
  137. r
  138. s
  139. [
  140. l
  141. o
  142. c
  143. a
  144. l
  145. T
  146. o
  147. k
  148. e
  149. n
  150. ]
  151. [
  152. r
  153. e
  154. m
  155. o
  156. t
  157. e
  158. T
  159. o
  160. k
  161. e
  162. n
  163. ]
  164.  
  165. =
  166. =
  167.  
  168. 0
  169. ,
  170.  
  171. .
  172. .
  173. .
  174. )
  175. `
  176.  
  177. v
  178. e
  179. y
  180. a
  181.  
  182. b
  183. e
  184. n
  185. z
  186. e
  187. r
  188.  
  189. t
  190. e
  191. k
  192. -
  193. s
  194. e
  195. f
  196. e
  197. r
  198. l
  199. i
  200. k
  201. /
  202. i
  203. d
  204. e
  205. m
  206. p
  207. o
  208. t
  209. e
  210. n
  211. c
  212. y
  213.  
  214. k
  215. o
  216. n
  217. t
  218. r
  219. o
  220. l
  221. u
  222.  
  223. o
  224. l
  225. m
  226. a
  227. d
  228. i
  229. g
  230. i
  231.  
  232. d
  233. o
  234. g
  235. r
  236. u
  237. l
  238. a
  239. n
  240. a
  241. b
  242. i
  243. l
  244. i
  245. r
  246.  
  247. -
  248. -
  249.  
  250. b
  251. u
  252. ,
  253.  
  254. S
  255. o
  256. l
  257. i
  258. d
  259. i
  260. t
  261. y
  262.  
  263. d
  264. i
  265. l
  266. i
  267. n
  268. i
  269. n
  270.  
  271. k
  272. e
  273. n
  274. d
  275. i
  276. s
  277. i
  278. y
  279. l
  280. e
  281.  
  282. d
  283. o
  284. g
  285. r
  286. u
  287. l
  288. a
  289. n
  290. a
  291. n
  292.  
  293. k
  294. e
  295. s
  296. i
  297. n
  298.  
  299. b
  300. i
  301. r
  302.  
  303. s
  304. t
  305. a
  306. t
  307. i
  308. k
  309.  
  310. g
  311. e
  312. r
  313. c
  314. e
  315. k
  316.  
  317. (
  318. c
  319. a
  320. l
  321. i
  322. s
  323. t
  324. i
  325. r
  326. m
  327. a
  328.  
  329. g
  330. e
  331. r
  332. e
  333. k
  334. t
  335. i
  336. r
  337. m
  338. e
  339. z
  340. )
  341. .
  342.  
  343. `
  344. f
  345. i
  346. n
  347. a
  348. l
  349. i
  350. z
  351. e
  352. T
  353. r
  354. a
  355. n
  356. s
  357. f
  358. e
  359. r
  360. (
  361. )
  362. `
  363. '
  364. d
  365. a
  366. k
  367. i
  368.  
  369. `
  370. $
  371. .
  372. d
  373. e
  374. p
  375. o
  376. s
  377. i
  378. t
  379. s
  380. [
  381. .
  382. .
  383. .
  384. ]
  385.  
  386. -
  387. =
  388.  
  389. l
  390. o
  391. c
  392. a
  393. l
  394. A
  395. m
  396. o
  397. u
  398. n
  399. t
  400. `
  401.  
  402. s
  403. a
  404. t
  405. i
  406. r
  407. i
  408. n
  409. i
  410. n
  411. ,
  412.  
  413. d
  414. e
  415. p
  416. o
  417. s
  418. i
  419. t
  420. s
  421. '
  422. i
  423. n
  424.  
  425. G
  426. E
  427. C
  428. M
  429. I
  430. S
  431.  
  432. T
  433. U
  434. M
  435.  
  436. b
  437. i
  438. r
  439. i
  440. k
  441. i
  442. m
  443. i
  444. n
  445. i
  446.  
  447. (
  448. h
  449. a
  450. n
  451. g
  452. i
  453.  
  454. s
  455. c
  456. a
  457. l
  458. a
  459. r
  460.  
  461. i
  462. l
  463. e
  464.  
  465. o
  466. l
  467. u
  468. r
  469. s
  470. a
  471.  
  472. o
  473. l
  474. s
  475. u
  476. n
  477. )
  478.  
  479. T
  480. U
  481. T
  482. T
  483. U
  484. G
  485. U
  486. N
  487. U
  488.  
  489. v
  490. e
  491.  
  492. s
  493. c
  494. a
  495. l
  496. a
  497. r
  498.  
  499. D
  500. E
  501. G
  502. I
  503. S
  504. T
  505. I
  506. G
  507. I
  508. N
  509. D
  510. E
  511.  
  512. b
  513. u
  514.  
  515. b
  516. i
  517. r
  518. i
  519. k
  520. i
  521. m
  522. i
  523. n
  524.  
  525. y
  526. e
  527. n
  528. i
  529. d
  530. e
  531. n
  532.  
  533. o
  534. l
  535. c
  536. e
  537. k
  538. l
  539. e
  540. n
  541. m
  542. e
  543. d
  544. i
  545. g
  546. i
  547. n
  548. i
  549.  
  550. d
  551. o
  552. g
  553. r
  554. u
  555. l
  556. a
  557. m
  558. a
  559. k
  560.  
  561. i
  562. c
  563. i
  564. n
  565.  
  566. `
  567. _
  568. a
  569. d
  570. d
  571. T
  572. o
  573. D
  574. e
  575. p
  576. o
  577. s
  578. i
  579. t
  580. s
  581. (
  582. )
  583. `
  584.  
  585. (
  586. T
  587. o
  588. k
  589. e
  590. n
  591. L
  592. i
  593. b
  594. .
  595. s
  596. o
  597. l
  598. )
  599.  
  600. i
  601. n
  602. c
  603. e
  604. l
  605. e
  606. n
  607. e
  608. b
  609. i
  610. l
  611. i
  612. r
  613.  
  614. -
  615. -
  616.  
  617. d
  618. e
  619. p
  620. o
  621. s
  622. i
  623. t
  624. s
  625. ,
  626.  
  627. S
  628. A
  629. D
  630. E
  631. C
  632. E
  633.  
  634. y
  635. e
  636. r
  637. e
  638. l
  639.  
  640. (
  641. l
  642. o
  643. c
  644. a
  645. l
  646. T
  647. o
  648. k
  649. e
  650. n
  651.  
  652. b
  653. i
  654. r
  655. i
  656. m
  657. i
  658. )
  659.  
  660. m
  661. i
  662. k
  663. t
  664. a
  665. r
  666. i
  667.  
  668. t
  669. u
  670. t
  671. u
  672. y
  673. o
  674. r
  675. ,
  676.  
  677. h
  678. a
  679. n
  680. g
  681. i
  682.  
  683. s
  684. c
  685. a
  686. l
  687. a
  688. r
  689.  
  690. i
  691. l
  692. e
  693.  
  694. h
  695. e
  696. s
  697. a
  698. p
  699. l
  700. a
  701. n
  702. d
  703. i
  704. g
  705. i
  706. n
  707. i
  708.  
  709. K
  710. A
  711. Y
  712. D
  713. E
  714. T
  715. M
  716. I
  717. Y
  718. O
  719. R
  720. .

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
`TokenLib.registerRemoteToken()` (base/src/libraries/TokenLib.sol) unconditionally overwrites `scalars[localToken][remoteToken]` with no guard against re-registration of an already-set pair. This function is reachable via `Bridge.__relayMessage()` whenever an incoming message's sender equals `REMOTE_BRIDGE`, gated only by the same `BridgeValidator` oracle/validator-multisig threshold that gates every other incoming message.

`finalizeTransfer()`'s lock/unlock paths (native ETH and native ERC20 'bridging back to EVM') compute `localAmount = transfer.remoteAmount * scalar` and decrement the AGGREGATE historical `deposits[localToken][remoteToken]` ledger by that amount. Because `deposits` accumulates local-unit value across the pair's entire history regardless of which scalar was in effect at deposit time, and because the scalar itself is freely overwritable, a single malicious-or-erroneous `registerRemoteToken` message that sets an inflated `scalarExponent` permanently corrupts the exchange rate for that pair. The very next `finalizeTransfer` message -- even one carrying a tiny `remoteAmount` -- can then drain the ENTIRE historical deposit pool for that token pair in one transaction, not just the value represented by the message itself. This converts what should be a bounded, single-message fraud (requiring the same oracle-signature threshold as any other bridge message) into an unbounded, pool-wide drain, dramatically amplifying the blast radius of any single bad registration -- whether from active oracle compromise/collusion or from an honest operational bug on the trusted Solana-side relayer that re-sends a stale/incorrect registration event.

Suggested fix: make scalar registration one-time-only per (localToken, remoteToken) pair, e.g. `require($.scalars[localToken][remoteToken] == 0, ScalarAlreadyRegistered());` before the assignment, or route scalar changes through a separate, more heavily-guarded/governance-gated path distinct from ordinary oracle-attested message relaying.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._