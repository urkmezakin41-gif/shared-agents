# 3 Aşamalı Bug Bounty Pipeline

```
[Tetikleyici]                 [Stage 1]              [Stage 2]                [Stage 3]
scan.sh --target X   ──▶   recon-and-auditor   ──▶  skeptical-triager   ──▶  dispatch.py
--scope "<yetki>"          (ajan, JSON taslak)      (ajan, confidence)      (deterministik script)
                                                                                   │
                                                                      reports/RAPOR_X.md
                                                                      (+ opsiyonel Telegram
                                                                       bildirimi, --notify)
```

## Tetikleme modeli

Bu pipeline **kendi kendine hedef seçip taramaz**. Zincir şöyle başlar:

1. Bir insan (siz) veya sizin kontrolünüzdeki bir süreç, belirli bir hedef
   için **açık bir yetki/scope beyanıyla** `scan.sh` çalıştırır:
   ```bash
   scripts/bugbounty/scan.sh --target <hedef> --scope "<yetki açıklaması>" [--github owner/repo]
   ```
   `--scope` zorunludur; boşsa script çalışmaz.
2. Ardından Claude'a (bu repoda) "pipeline'ı `<hedef>` için çalıştır" denir.
   Bu noktadan sonra 3 aşama **art arda, tekrar onay istemeden** çalışır:
   - `recon-and-auditor` ham veriyi okur → `stage1_findings.json` yazar.
   - `skeptical-triager` her adayı çürütmeye çalışır → `stage2_verdicts.json` yazar.
   - `dispatch.py` iki dosyayı birleştirir, yalnızca **confidence ≥ 90 ve
     verdict == PASS** olanları `reports/RAPOR_<hedef>.md`'ye yazar.

Bu, "otomasyon" isteğini karşılar: aşamalar arası elle kopyala-yapıştır
yok, hepsi tek bir istekle zincirlenir. Değişmeyen şey: **hedef seçimi ve
ilk tetikleme her zaman bir insan eylemidir** — zamanlanmış/periyodik bir
tetikleyici yoktur, çünkü her hedef için ayrı bir yetki beyanı gerekir.

## Neden resmi platforma otomatik gönderim yok

`dispatch.py` ve `report-dispatcher` agent'ı **hiçbir koşulda** GitHub
Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik
çağrı yapmaz — `GITHUB_TOKEN` veya `HACKERONE_API_TOKEN` ortamda olsa bile.

* Resmi bir disclosure kanalına gönderim **geri alınamaz**: tekrar
  gönderilemez, program kurallarını ihlal edebilir (scope dışı/mükerrer
  rapor), itibar etkisi olabilir. Bir LLM'in kendine verdiği confidence
  skoru bunu tek başına meşrulaştırmaz — bu yüzden gönderim daima ayrı,
  insan tarafından teyit edilen bir adımdır.
* HackerOne'ın üçüncü taraf araştırmacılar için genel/güvenilir bir
  "rapor oluştur" public API'si olduğundan emin değiliz. Var olmadığından
  veya farklı davrandığından emin olunmayan bir API çağrısını "gönderildi"
  diye raporlamak, emirnamenin Zero-Hallucination ilkesini bizzat scriptin
  kendisinde ihlal eder.

Bunun yerine `reports/RAPOR_<hedef>.md` içindeki her geçen bulgu için
**kopyala-yapıştır'a hazır İngilizce HackerOne/Immunefi taslağı** zaten
üretilmiş durumda. Gönderim adımı: raporu okuyun, onaylayın, ilgili
platforma (HackerOne web formu, GitHub'ın "Report a vulnerability" UI'ı,
Immunefi) kendiniz yapıştırın.

## Telegram bildirimi

`dispatch.py --notify`, yalnızca `TELEGRAM_BOT_TOKEN` ve
`TELEGRAM_CHAT_ID` ortam değişkenleri **varsa**, üretilen `.md` dosyasını
Telegram'a gönderir. Bu bir **bildirim**dir (sizin kendi botunuza,
incelemeniz için) — hiçbir resmi disclosure platformuna gönderim değildir.
Env değişkenleri yoksa adım sessizce atlanır, hata vermez.

## Dosya/veri akışı

```
scripts/bugbounty/out/<hedef>/
├── raw/                      # scan.sh çıktısı (ham veri, repoya commitlenmez)
├── stage1_findings.json      # Stage 1 çıktısı
└── stage2_verdicts.json      # Stage 2 çıktısı

reports/RAPOR_<hedef>.md      # Stage 3 çıktısı — tek commitlenen sonuç
```

`scripts/bugbounty/out/` tamamen `.gitignore`'da; yalnızca nihai
`reports/RAPOR_*.md` repoya girer.

## Test

`dispatch.py`, aşağıdaki iki senaryoyla uydurma (sentetik, açıkça test
amaçlı işaretli) fixture verisiyle test edildi:
* 2 adaydan 1'inin eşiği geçtiği, diğerinin reddedildiği bir rapor —
  geçen bulgu tam detayla, reddedilen bulgu yalnızca bir özet tablosunda
  (içeriği olmadan) göründü.
* 0 adayla "temiz" rapor — `[⚪ TEMİZ - GEÇ]` doğru üretildi.
* `--notify` bayrağı, Telegram env değişkenleri yokken hatasız atlandı.

Resmi bir platforma gerçek gönderim **test edilmedi ve edilmeyecek** —
böyle bir testin kendisi gerçek, geri alınamaz bir rapor dosyalaması
anlamına gelirdi.
