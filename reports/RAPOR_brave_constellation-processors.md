# Bug Bounty Raporu — brave_constellation-processors

**Tarih:** 2026-11-04 08:45 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) — Exact 1-to-1 Wildcard SOURCE_CODE Asset Identifier: brave -> https://github.com/brave/constellation-processors (structured_scope id: 943222, eligible_for_bounty: true, max_severity: critical). Language: Rust. Description: Server-side collector and aggregator for recovering data protected by the Constellation/nested STAR protocol.
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave_constellation-processors/raw`
* **Engellenen/erişilemeyen adımlar:** KRITIK SINIRLAMA: `star_constellation` ve `star-sharks` crate'lerinin (Shamir/eşik-tabanli secret-sharing'in GERCEK matematigini -- `key_recover`/`recover`/`client::construct_message` fonksiyonlarinin ic-yuzu) KAYNAK KODU bu teslimde YOK (harici bagimlilik). Bulgumun DOGRULUGU, 'bir TAG icin reconstruct edilen anahtarin, hangi ESIK (k) degeriyle/hangi mesaj KUMESIYLE reconstruct edildiginden BAGIMSIZ olarak AYNI (TAG'a baglı, OPRF-turevi) deger oldugu' varsayimina DAYANIYOR -- bu varsayim, kodun KENDI yapisindan (asagida detaylandirilan) GUCLU sekilde CIKARILIYOR ama harici kripto-kutuphanenin kaynak kodu OLMADAN %100 KANITLANAMIYOR. Bu nedenle bulgu, YUKSEK-GUVENSIZLIK ama ACIK CAVEAT'li olarak sunuluyor.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* Hedef, Brave'in Nested STAR / Constellation gizlilik-koruyucu telemetri protokolunun SUNUCU-TARAFI toplayici/aggregator'u -- cok sayida kullanicidan gelen 'STAR mesajlarini' toplayip, SADECE en az k (esik) BAGIMSIZ kullanici AYNI degeri raporladiginda o degeri acığa cikaran bir k-anonimlik mekanizmasi. Bu, bu oturumdaki challenge-bypass-ristretto ailesiyle AYNI 'gizlilik-kritik kripto protokolu' sinifinda, ve kalici kisitlama (hic PoC/exploit kodu URETME) BURADA DA TAM OLARAK uygulandi -- SADECE statik kod-okumasi/kontrol-akisi analizi yapildi, HICBIR calistirma/network-istegi GIRISIMI OLMADI.
* Iki commit diff'i (eb2e093e6d: CI pin-guncellemesi; 33d0e7b902: Cargo.lock BAGIMLILIK-GUNCELLEMESI + `cargo audit --deny warnings` -> `cargo audit` (CI'nin bagimlilik-uyari-SERTLIGININ gevsetilmesi, ANCAK bu salt bir CI-politika degisikligi, uretim KODUNDA bir guvenlik REGRESYONU DEGIL)) incelendi -- HER IKISI DE guvenlik acisindan NOTR/IYILESTIRME niteliginde.
* F1, bu oturumun EN ONEMLI/EN CIDDI potansiyel bulgusu -- ANCAK dogrulugu, harici `star_constellation`/`star-sharks` crate'lerinin (teslim edilmeyen) kripto matematigine BAGLI. Kod-seviyesindeki YAPISAL gercek (bir kovanin anahtari, TUM diger kovalara UYGULANIYOR, esik-bagimsiz) KESIN olarak dogrulandi; crypto-varsayim DOGRULANAMADI.
* `src/star.rs`'teki `recover_key()`'in `msgs_to_use = min(k_threshold + k_threshold/3, messages.len())` ile SECTIGI 'fazladan' (k/3) mesaj SAYISI, muhtemelen Shamir reconstruction'da BOZUK/kotu-niyetli PAYLARA karsi HATA-TOLERANSI (redundancy) icin -- bu KENDI BASINA bir zafiyet DEGIL, ayri bir TASARIM notu.
* `src/aggregator/group.rs`, `src/aggregator/processing.rs`, `src/server.rs`, `src/aggregator/consume.rs`, `src/star.rs` dosyalarinin TAMAMI (test kodlari DAHIL) satir-satir okundu. `src/aggregator/recovered.rs`, `src/aggregator/report.rs`, `src/lake.rs`, `src/lakesink.rs`, `src/scheduler.rs`, `src/record_stream.rs` (Kafka/AWS/veri-golu entegrasyon dosyalari) ZAMAN KISITI nedeniyle SADECE goz-gezdirme seviyesinde incelendi -- bu dosyalarda ayrica bir bulgu ARANMADI.

## 📊 Bulgu F1: aggregator/processing.rs::process_one_layer(): bir ETIKET (tag) icin BIR eşik-kovasinin (kendi, ISTEMCI-TARAFINDAN SECILEBILEN esigini karsilayan) anahtari reconstruct etmesi, AYNI etiketin TUM DIGER eşik-kovalarindaki (KENDI eşiklerini HENUZ KARSILAMAMIS) mesajlarin da COZULMESINE (recover_msgs) yol aciyor -- bu, Nested STAR protokolunun k-anonimlik esigini, saldirganin kontrol edebildigi [MIN_REQUEST_K_THRESHOLD, MAX_REQUEST_K_THRESHOLD] araligindaki (varsayilan [20, 50]) herhangi bir DEGERE dusurebilmesine izin verebilir
* **Durum:** `[⚠️ İNCELENMELİ (ORTA/YÜKSEK)]`
* **Tahmini Önem Derecesi:** critical (eger varsayim DOGRU ise -- Nested STAR'in TEMEL gizlilik garantisini BYPASS ediyor), ancak harici kripto-kutuphanenin dogrulanamamasi nedeniyle confidence SINIRLI
* **Zafiyet Sınıfı (CWE):** CWE-284 (Improper Access Control) / k-anonimlik/esik-gecersiz-kilma -- gizlilik bypass'i
* **Stage 2 Confidence:** 45/100 — Kod-seviyesi YAPISAL iddiayi (bir eşik-kovasinin anahtari, AYNI etiketin TUM diger kovalarina -- kendi esiklerini karsilayip-karsilamadigina bakilmadan -- uygulaniyor) CURUTMEYE calistim ve BASARISIZ oldum: processing.rs'teki `for threshold in thresholds { ...; recover_msgs(msgs, &key)?; }` dongusu, GERCEKTEN `threshold == recovery_threshold` KOSULUNU KONTROL ETMIYOR (sadece HANGI mesaj-vektorunun zaten-drain-edilmis-olup-olmadigini kontrol ediyor) -- TUM kovalar AYNI anahtarla cozuluyor, bu KESIN. server.rs'teki `request_threshold_range` (varsayilan [20,50]) kontrolu de DOGRU okundu -- istemci GERCEKTEN sunucunun KENDI varsayilan esiginden (50) DAHA DUSUK bir deger (20) SECEBILIYOR. Bu IKI gercek birlesince, YAPISAL zafiyet SAGLAM duruyor.

REJECT'E ITMEYE calistigim ama BASARILI OLAMADIGIM itirazlar: (1) 'Belki client kutuphanesi, k_threshold'u mesajin KENDI icine KRIPTOGRAFIK olarak GOMUYOR ve SUNUCU bunu DOGRULUYOR' -- ARANDI, `recover_key`/`key_recover` imzasinda boyle bir CAPRAZ-DOGRULAMA GORULMEDI (sadece `epoch_tag` ve mesaj listesi aliniyor, 'bu mesajlarin HANGI k ile uretildigi' AYRICA DOGRULANMIYOR GORUNUYOR) -- ama bu NIHAI olarak KANITLANAMAZ (crate kaynagi YOK). (2) 'Belki saldirgan tag'i BILEMEZ, bu nedenle PRATIK degeri YOK' -- KISMEN DOGRU (saldirgan HEDEF olcum-degerini ONCEDEN bilmek/tahmin etmek ZORUNDA), ANCAK bu, Nested STAR'in COK SAYIDA pratik kullanim-SENARYOSUNDA (orn. belirli bir URL/extension-id/user-agent gibi, saldirganin ZATEN BILDIGI veya KUCUK bir KUME icinden TAHMIN edebildigi dusuk-kardinaliteli degerler) GECERLI bir SINIRLAMA degil -- confidence'i DUSURUYOR ama SIFIRLAMIYOR. (3) 'Belki `MIN_REQUEST_K_THRESHOLD` PRODUKSIYONDA cok DAHA YUKSEK bir degere AYARLANMIS (orn. =K_THRESHOLD, esitligi ZORUNLU kilacak sekilde)' -- bu TAMAMEN MUMKUN ve bu teslimde DOGRULANAMAZ (bu bir deployment-config/env-degiskeni, kod KENDISI varsayimi =20 olarak BIRAKIYOR, ki bu K_THRESHOLD=50'DEN KESIN OLARAK DUSUK) -- EGER produksiyonda MIN=MAX=K_THRESHOLD ayarlanmissa, bu zafiyet PRATIKTE SIFIRLANIR, ama KOD KENDI BASINA bunu ZORUNLU KILMIYOR (varsayilan deger farkli).

PASS karari, YAPISAL kod-akisi iddiasinin DOGRULUGU + bunun DOGRU olmasi durumunda SONUCUN (k-anonimlik ihlali) KRITIK OLMASI uzerine KURULU. Confidence'i 45'te (orta, PASS esiginin HAFIFCE uzerinde) TUTUYORUM -- cunku NIHAI dogrulama harici bir crypto-kutuphaneye BAGLI ve bu teslimde YOK, VE varsayilan MIN_REQUEST_K_THRESHOLD'un gercek-produksiyon degeri BELIRSIZ. Bu, 'base_bridge' PASS kararindaki (confidence 65, 'amplifikasyon ama temel-guven-sinirini ASMIYOR') orneginden DAHA BELIRSIZ bir durum, ama 'base_onchainsummer.xyz' (confidence 55, somut ucuncu-taraf etkisi) orneginden DAHA CIDDI bir POTANSIYEL SONUC tasiyor -- bu ikisinin ARASINA, hafif-PASS-esigi-uzerine KONUMLANDIRDIM.

### 🔍 Teknik Kanıt ve Kod Analizi
* **Sorunlu Dosya / Uç Nokta / Satır:** src/aggregator/processing.rs::process_one_layer() (satir ~2932-3026, ozellikle 2961-2973 'for threshold in thresholds' dongusu) + src/aggregator/group.rs::MessageChunk::recoverable_threshold() + src/server.rs::handle_measurement_submit() (satir ~7449-7454, THRESHOLD_HEADER dogrulamasi) + src/aggregator/consume.rs (satir ~1968, `threshold: record.request_threshold.unwrap_or(default_k_threshold)`)
* **Kanıt kaynağı:** `src/aggregator/processing.rs`
* **Kanıt alıntısı:**
  ```
  let recovery_threshold = chunk.recoverable_threshold();
...
let (key, mut key_recovery_msgs) = match get_recovery_key(*epoch, chunk, recovery_threshold, existing_rec_msg.as_ref())? { ... };
...
let mut thresholds = HashSet::new();
thresholds.extend(chunk.new_msgs.keys().chain(chunk.pending_msgs.keys()));

// recover each k-threshold group separately so we store
// new nested pending messages with the correct threshold value
for threshold in thresholds {
  let msgs = if recovery_threshold == Some(threshold) && key_recovery_msgs.is_some() {
    key_recovery_msgs.take().unwrap()
  } else {
    drain_chunk_messages_for_threshold(chunk, threshold)?
  };
  if msgs.is_empty() { continue; }
  let MsgRecoveryInfo { measurement, next_layer_messages, error_count } = recover_msgs(msgs, &key)?;
  ...
  ```
* **Neden Güvenlik Açığı Oluşuyor?:** Sistem, AYNI etikete (tag -- ayni olculen degeri/mesaji temsil eden, OPRF-turevi deterministik bir deger) sahip mesajlari, HER MESAJIN KENDI TASIDIGI 'threshold' (esik) alanina GORE AYRI KOVALARA (`MessageChunk.new_msgs: HashMap<usize, Vec<NestedMessage>>`) AYIRIYOR. Bu 'threshold' alani, `src/aggregator/consume.rs` satir 1968'de goruldugu uzere `record.request_threshold.unwrap_or(default_k_threshold)` -- yani ISTEMCININ (gelen HTTP istegindeki `Brave-P3A-Constellation-Threshold` basligi araciligiyla, `src/server.rs`'teki `THRESHOLD_HEADER` kontrolu) KENDI SECTIGI bir DEGER, SADECE `[MIN_REQUEST_K_THRESHOLD, MAX_REQUEST_K_THRESHOLD]` (varsayilan `[20, 50]`) ARALIGINA KIRPILIYOR (server.rs ~7451: `if !state.request_threshold_range.contains(&threshold) { return Err(BadThreshold) }`). Yani bir ISTEMCI (saldirgan), varsayilan sunucu-esigi (`K_THRESHOLD=50`) yerine, KENDI GONDERDIGI mesaj(lar) icin ARALIGIN EN KUCUK degerini (varsayilan 20) SECEBILIR.

`process_one_layer()` fonksiyonu, bir etiketin ('tag') ILGILI `MessageChunk`'inda, `recoverable_threshold()` HERHANGI BIR eşik-kovasinin (`new_msgs[k] + pending_msgs[k] >= k`) KARSILANDIGINI bulursa, O KOVANIN mesajlarindan bir ANAHTAR (key) reconstruct ediyor (`get_recovery_key`). KRITIK OLAN KISIM: anahtar BIR KERE elde edildikten SONRA, kod BU ANAHTARI, AYNI etikete ait TUM DIGER esik-kovalarindaki (`chunk.new_msgs.keys().chain(chunk.pending_msgs.keys())` -- yani KENDI esiklerini HENUZ karsilamamis, 'pending' durumdaki HER kova DAHIL) mesajlari DA `recover_msgs(msgs, &key)` ile cozmek icin KULLANIYOR -- HICBIR koşul, 'bu DIGER kovanin da KENDI esigini karsilayip-karsilamadigini' KONTROL ETMIYOR; `drain_chunk_messages_for_threshold` sadece o kovadaki (kac mesaj OLURSA OLSUN, 1 dahi olsa) TUM mesajlari CEKIYOR ve HEMEN cozuluyor.

Bu, EGER (kodun kendi ic-tutarliligindan guclu sekilde CIKARILAN, ama harici kripto-kutuphane olmadan %100 DOGRULANAMAYAN) kripto-varsayim DOGRUYSA -- yani bir TAG icin reconstruct edilen 'anahtar', HANGI eşik-degeriyle/HANGI mesaj-ALT-KUMESIYLE reconstruct edildiginden BAGIMSIZ olarak AYNI (o TAG'a/OPRF-ciktisina BAGLI) deger ise -- ASAGIDAKI SALDIRI MUMKUNDUR: Bir saldirgan, HEDEF bir olcum-degeri (measurement) icin (bu degeri ONCEDEN BILMESI/TAHMIN ETMESI GEREKIYOR, cunku tag=OPRF(measurement, epoch) deterministik) en AZ 20 (MIN_REQUEST_K_THRESHOLD) SAHTE/kendi-urettigi mesaj GONDERIR, HER BIRINDE `Brave-P3A-Constellation-Threshold: 20` basligiyla. Bu 20 mesaj kendi kovasinda (`new_msgs[20]`) toplanir VE `recoverable_threshold()` bunu HEMEN 'karsilanmis' olarak isaretler (20 mesaj >= 20 esik) -- anahtar BU 20 SAHTE mesajdan reconstruct edilir. ARDINDAN, AYNI tag'e ait, GERCEK kullanicilarin (varsayilan `K_THRESHOLD=50` ile, HENUZ 50'YE ULASMAMIS, orn. sadece 3-5 GERCEK kullanicidan olusan) 'pending' kovasi, BU AYNI anahtarla COZULUR -- VE o olcumun EN AZ 3-5 GERCEK kullanici tarafindan raporlandigi, ASIL k=50 anonimlik-esigine HIC ULASILMADAN ORTAYA CIKARILIR. Bu, Nested STAR'in TEMEL guvenlik vaadini ('bir olcum degeri, EN AZ k BAGIMSIZ kullanici raporlamadikca SUNUCU TARAFINDAN OGRENILEMEZ') DOGRUDAN IHLAL eder. AYRICA, eger bu ETIKETIN alt-katmanlari (`next_layer_messages`) varsa, bu YANLIS-ERKEN cozulen anahtar, GERCEK kullanicilarin alt-katman mesajlarinin da DESIFRE EDILIP bir sonraki katmana AKTARILMASINA yol acar -- potansiyel olarak BU SALDIRIYI (daha dusuk esikli SAHTE kardes-mesajlarla) HER KATMANDA TEKRARLAYARAK, nihayetinde TEK bir kullanicinin EN DETAYLI/en kimlik-belirleyici verisine KADAR inilebilir.
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
  46. (
  47. 1
  48. )
  49.  
  50. `
  51. s
  52. e
  53. r
  54. v
  55. e
  56. r
  57. .
  58. r
  59. s
  60. `
  61. '
  62. t
  63. e
  64. k
  65. i
  66.  
  67. `
  68. r
  69. e
  70. q
  71. u
  72. e
  73. s
  74. t
  75. _
  76. t
  77. h
  78. r
  79. e
  80. s
  81. h
  82. o
  83. l
  84. d
  85. _
  86. r
  87. a
  88. n
  89. g
  90. e
  91. `
  92.  
  93. k
  94. o
  95. n
  96. t
  97. r
  98. o
  99. l
  100. u
  101. n
  102. u
  103. n
  104.  
  105. S
  106. A
  107. D
  108. E
  109. C
  110. E
  111.  
  112. `
  113. [
  114. M
  115. I
  116. N
  117. _
  118. R
  119. E
  120. Q
  121. U
  122. E
  123. S
  124. T
  125. _
  126. K
  127. _
  128. T
  129. H
  130. R
  131. E
  132. S
  133. H
  134. O
  135. L
  136. D
  137. =
  138. 2
  139. 0
  140. ,
  141.  
  142. M
  143. A
  144. X
  145. _
  146. R
  147. E
  148. Q
  149. U
  150. E
  151. S
  152. T
  153. _
  154. K
  155. _
  156. T
  157. H
  158. R
  159. E
  160. S
  161. H
  162. O
  163. L
  164. D
  165. =
  166. 5
  167. 0
  168. ]
  169. `
  170.  
  171. a
  172. r
  173. a
  174. l
  175. i
  176. g
  177. i
  178. n
  179. i
  180.  
  181. Z
  182. O
  183. R
  184. U
  185. N
  186. L
  187. U
  188.  
  189. k
  190. i
  191. l
  192. d
  193. i
  194. g
  195. i
  196. ,
  197.  
  198. D
  199. E
  200. F
  201. A
  202. U
  203. L
  204. T
  205.  
  206. s
  207. u
  208. n
  209. u
  210. c
  211. u
  212.  
  213. e
  214. s
  215. i
  216. g
  217. i
  218.  
  219. `
  220. K
  221. _
  222. T
  223. H
  224. R
  225. E
  226. S
  227. H
  228. O
  229. L
  230. D
  231. =
  232. 5
  233. 0
  234. `
  235. '
  236. d
  237. e
  238. n
  239.  
  240. D
  241. U
  242. S
  243. U
  244. K
  245.  
  246. b
  247. i
  248. r
  249.  
  250. d
  251. e
  252. g
  253. e
  254. r
  255.  
  256. (
  257. 2
  258. 0
  259. )
  260.  
  261. S
  262. E
  263. C
  264. I
  265. L
  266. E
  267. B
  268. I
  269. L
  270. D
  271. I
  272. G
  273. I
  274.  
  275. D
  276. O
  277. G
  278. R
  279. U
  280. L
  281. A
  282. N
  283. D
  284. I
  285.  
  286. (
  287. d
  288. o
  289. g
  290. r
  291. u
  292. d
  293. a
  294. n
  295.  
  296. s
  297. a
  298. b
  299. i
  300. t
  301. -
  302. d
  303. e
  304. g
  305. e
  306. r
  307. l
  308. e
  309. r
  310.  
  311. k
  312. a
  313. r
  314. s
  315. i
  316. l
  317. a
  318. s
  319. t
  320. i
  321. r
  322. i
  323. l
  324. d
  325. i
  326. )
  327. .
  328.  
  329. (
  330. 2
  331. )
  332.  
  333. `
  334. g
  335. r
  336. o
  337. u
  338. p
  339. .
  340. r
  341. s
  342. :
  343. :
  344. r
  345. e
  346. c
  347. o
  348. v
  349. e
  350. r
  351. a
  352. b
  353. l
  354. e
  355. _
  356. t
  357. h
  358. r
  359. e
  360. s
  361. h
  362. o
  363. l
  364. d
  365. (
  366. )
  367. `
  368. '
  369. i
  370. n
  371.  
  372. H
  373. E
  374. R
  375.  
  376. e
  377. ş
  378. i
  379. k
  380. -
  381. k
  382. o
  383. v
  384. a
  385. s
  386. i
  387. n
  388. i
  389.  
  390. (
  391. f
  392. a
  393. r
  394. k
  395. l
  396. i
  397.  
  398. '
  399. t
  400. h
  401. r
  402. e
  403. s
  404. h
  405. o
  406. l
  407. d
  408. '
  409.  
  410. d
  411. e
  412. g
  413. e
  414. r
  415. l
  416. e
  417. r
  418. i
  419. )
  420.  
  421. B
  422. A
  423. G
  424. I
  425. M
  426. S
  427. I
  428. Z
  429.  
  430. o
  431. l
  432. a
  433. r
  434. a
  435. k
  436.  
  437. k
  438. o
  439. n
  440. t
  441. r
  442. o
  443. l
  444.  
  445. e
  446. t
  447. t
  448. i
  449. g
  450. i
  451. ,
  452.  
  453. v
  454. e
  455.  
  456. `
  457. p
  458. r
  459. o
  460. c
  461. e
  462. s
  463. s
  464. i
  465. n
  466. g
  467. .
  468. r
  469. s
  470. :
  471. :
  472. p
  473. r
  474. o
  475. c
  476. e
  477. s
  478. s
  479. _
  480. o
  481. n
  482. e
  483. _
  484. l
  485. a
  486. y
  487. e
  488. r
  489. (
  490. )
  491. `
  492. '
  493. i
  494. n
  495. ,
  496.  
  497. H
  498. E
  499. R
  500. H
  501. A
  502. N
  503. G
  504. I
  505.  
  506. B
  507. I
  508. R
  509.  
  510. k
  511. o
  512. v
  513. a
  514.  
  515. '
  516. h
  517. a
  518. z
  519. i
  520. r
  521. '
  522.  
  523. o
  524. l
  525. d
  526. u
  527. g
  528. u
  529. n
  530. d
  531. a
  532.  
  533. e
  534. l
  535. d
  536. e
  537.  
  538. e
  539. d
  540. i
  541. l
  542. e
  543. n
  544.  
  545. T
  546. E
  547. K
  548.  
  549. b
  550. i
  551. r
  552.  
  553. a
  554. n
  555. a
  556. h
  557. t
  558. a
  559. r
  560. i
  561.  
  562. (
  563. `
  564. k
  565. e
  566. y
  567. `
  568. )
  569. ,
  570.  
  571. S
  572. O
  573. N
  574. R
  575. A
  576. S
  577. I
  578. N
  579. D
  580. A
  581.  
  582. `
  583. t
  584. h
  585. r
  586. e
  587. s
  588. h
  589. o
  590. l
  591. d
  592. s
  593. `
  594.  
  595. k
  596. u
  597. m
  598. e
  599. s
  600. i
  601. n
  602. d
  603. e
  604. k
  605. i
  606.  
  607. T
  608. U
  609. M
  610.  
  611. k
  612. o
  613. v
  614. a
  615. l
  616. a
  617. r
  618. a
  619.  
  620. (
  621. k
  622. e
  623. n
  624. d
  625. i
  626.  
  627. e
  628. s
  629. i
  630. g
  631. i
  632. n
  633. i
  634.  
  635. k
  636. a
  637. r
  638. s
  639. i
  640. l
  641. a
  642. m
  643. i
  644. s
  645.  
  646. v
  647. e
  648. y
  649. a
  650.  
  651. K
  652. A
  653. R
  654. S
  655. I
  656. L
  657. A
  658. M
  659. A
  660. M
  661. I
  662. S
  663.  
  664. A
  665. Y
  666. I
  667. R
  668. T
  669.  
  670. E
  671. T
  672. M
  673. E
  674. D
  675. E
  676. N
  677. )
  678.  
  679. u
  680. y
  681. g
  682. u
  683. l
  684. a
  685. d
  686. i
  687. g
  688. i
  689. ,
  690.  
  691. d
  692. o
  693. g
  694. r
  695. u
  696. d
  697. a
  698. n
  699.  
  700. k
  701. o
  702. d
  703. -
  704. o
  705. k
  706. u
  707. m
  708. a
  709. s
  710. i
  711. y
  712. l
  713. a
  714.  
  715. (
  716. D
  717. E
  718. G
  719. I
  720. S
  721. K
  722. E
  723. N
  724.  
  725. a
  726. k
  727. i
  728. s
  729. l
  730. a
  731. r
  732. i
  733.  
  734. t
  735. a
  736. k
  737. i
  738. p
  739.  
  740. e
  741. d
  742. i
  743. l
  744. e
  745. r
  746. e
  747. k
  748. )
  749.  
  750. D
  751. O
  752. G
  753. R
  754. U
  755. L
  756. A
  757. N
  758. D
  759. I
  760.  
  761. -
  762. -
  763.  
  764. b
  765. u
  766. ,
  767.  
  768. c
  769. a
  770. l
  771. i
  772. s
  773. t
  774. i
  775. r
  776. m
  777. a
  778.  
  779. G
  780. E
  781. R
  782. E
  783. K
  784. T
  785. I
  786. R
  787. M
  788. E
  789. Y
  790. E
  791. N
  792.  
  793. b
  794. i
  795. r
  796.  
  797. Y
  798. A
  799. P
  800. I
  801. S
  802. A
  803. L
  804.  
  805. g
  806. e
  807. r
  808. c
  809. e
  810. k
  811. .
  812.  
  813. C
  814. U
  815. R
  816. U
  817. T
  818. U
  819. L
  820. E
  821. M
  822. E
  823. Y
  824. E
  825. N
  826.  
  827. T
  828. E
  829. K
  830.  
  831. v
  832. a
  833. r
  834. s
  835. a
  836. y
  837. i
  838. m
  839. :
  840.  
  841. `
  842. k
  843. e
  844. y
  845. _
  846. r
  847. e
  848. c
  849. o
  850. v
  851. e
  852. r
  853. `
  854. '
  855. i
  856. n
  857.  
  858. G
  859. E
  860. R
  861. C
  862. E
  863. K
  864. T
  865. E
  866. N
  867.  
  868. e
  869. ş
  870. i
  871. k
  872. -
  873. B
  874. A
  875. G
  876. I
  877. M
  878. S
  879. I
  880. Z
  881. ,
  882.  
  883. S
  884. A
  885. D
  886. E
  887. C
  888. E
  889.  
  890. t
  891. a
  892. g
  893. '
  894. e
  895.  
  896. b
  897. a
  898. g
  899. l
  900. i
  901.  
  902. b
  903. i
  904. r
  905.  
  906. d
  907. e
  908. g
  909. e
  910. r
  911.  
  912. u
  913. r
  914. e
  915. t
  916. t
  917. i
  918. g
  919. i
  920.  
  921. -
  922. -
  923.  
  924. b
  925. u
  926. ,
  927.  
  928. h
  929. a
  930. r
  931. i
  932. c
  933. i
  934.  
  935. `
  936. s
  937. t
  938. a
  939. r
  940. _
  941. c
  942. o
  943. n
  944. s
  945. t
  946. e
  947. l
  948. l
  949. a
  950. t
  951. i
  952. o
  953. n
  954. `
  955.  
  956. c
  957. r
  958. a
  959. t
  960. e
  961. '
  962. i
  963. n
  964. i
  965. n
  966.  
  967. K
  968. A
  969. Y
  970. N
  971. A
  972. K
  973.  
  974. K
  975. O
  976. D
  977. U
  978.  
  979. O
  980. L
  981. M
  982. A
  983. D
  984. A
  985. N
  986.  
  987. N
  988. I
  989. H
  990. A
  991. I
  992.  
  993. o
  994. l
  995. a
  996. r
  997. a
  998. k
  999.  
  1000. K
  1001. A
  1002. N
  1003. I
  1004. T
  1005. L
  1006. A
  1007. N
  1008. A
  1009. M
  1010. A
  1011. Z
  1012.  
  1013. (
  1014. b
  1015. u
  1016.  
  1017. t
  1018. e
  1019. s
  1020. l
  1021. i
  1022. m
  1023. d
  1024. e
  1025.  
  1026. Y
  1027. O
  1028. K
  1029. )
  1030. .

### 📝 HackerOne / Immunefi Hazır Rapor Taslağı (İngilizce)

> ⚠️ Bu metin otomatik olarak hiçbir platforma GÖNDERİLMEDİ.
> İnceleyip onayladıktan sonra kendiniz kopyalayıp platforma yapıştırın.

```markdown
In `src/aggregator/processing.rs::process_one_layer()`, messages sharing the same STAR tag are bucketed by a per-message `threshold` value that originates from `record.request_threshold` (`src/aggregator/consume.rs` line ~1968), which in turn comes directly from a client-controlled HTTP header (`Brave-P3A-Constellation-Threshold`, validated in `src/server.rs::handle_measurement_submit` only against a configurable `[MIN_REQUEST_K_THRESHOLD, MAX_REQUEST_K_THRESHOLD]` range -- `20..=50` by default, versus the server's own default aggregation threshold `K_THRESHOLD=50`). `MessageChunk::recoverable_threshold()` (`src/aggregator/group.rs`) independently checks each threshold-bucket for whether it has reached its own declared count, and `process_one_layer()` reconstructs a key (`get_recovery_key`/`recover_key`) from WHICHEVER bucket is ready first. Critically, once this key is obtained, the code applies it (`recover_msgs(msgs, &key)`) to EVERY OTHER threshold-bucket present for the same tag -- including buckets that have NOT met their own declared threshold (`for threshold in thresholds { ... drain_chunk_messages_for_threshold(chunk, threshold)?; ...; recover_msgs(msgs, &key)?; }`), with no check that each bucket independently reached its own `k`. If the underlying Shamir/threshold key-recovery scheme (in the external `star_constellation`/`star-sharks` crates, not included in this delivery, so this could not be independently verified end-to-end) produces a key that depends only on the tag (the OPRF-derived value for a given measurement) rather than on which specific threshold-bucket or subset of shares was used to reconstruct it, then an attacker who already knows or can guess a target measurement value can submit as few as `MIN_REQUEST_K_THRESHOLD` (20 by default) self-crafted messages for that tag with the header set to the minimum allowed threshold (20), triggering premature key recovery, and that key would then also unlock -- and reveal the existence/count of -- any genuine users' submissions for the same measurement sitting in the server's own default-threshold (50) 'pending' bucket, even if far fewer than 50 real users have actually reported it. This would defeat Nested STAR's core k-anonymity guarantee (a measurement should never be revealed unless at least k independent clients reported it) for any attacker able to guess the target measurement value and submit ~20 crafted reports, and could cascade to deeper nested layers (more identifying sub-measurements) via the same mechanism applied to `next_layer_messages`. Please treat this as reported with significant uncertainty pending confirmation against the actual `key_recover`/`recover` cryptographic implementation (external crates not in this repository), but the control-flow structure described above is directly verifiable by reading the three files named. Suggested mitigation (pending crypto confirmation): either reject/ignore `request_threshold` entirely and always use the server's own fixed `K_THRESHOLD` for recovery decisions, or, when a key is recovered from one threshold-bucket, require that any OTHER threshold-bucket for the same tag independently satisfies its own declared threshold before being decrypted with that key.
```

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._