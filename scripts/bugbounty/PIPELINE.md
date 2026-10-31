# 3 Aşamalı Bug Bounty Pipeline

```
[Tetikleyici]                       [Ingest]        [Stage 1]            [Stage 2]              [Stage 3]
A) scan.sh --target X --scope  ──┐
B) incoming/*.json (git push)  ──┴─▶ ingest.py ─▶ recon-and-auditor ─▶ skeptical-triager ─▶ dispatch.py
                                      (scope          (ajan, JSON           (ajan,              (deterministik
                                       doğrulama)      taslak)              confidence)          script)
                                                                                                      │
                                                                                        reports/RAPOR_X.md
                                                                                        (+ opsiyonel Telegram
                                                                                         bildirimi, --notify,
                                                                                         yalnızca ÇIKIŞ)
```

## Tetikleme modeli

Bu pipeline **kendi kendine hedef seçip taramaz**. İki giriş kanalı var,
ikisi de veri içinde **zorunlu bir `scope_declaration` alanı** taşımak
zorunda — yoksa veri reddedilir, analiz edilmez:

* **A) Manuel (`scan.sh`):** İnsan, belirli bir hedef için
  `scan.sh --target <hedef> --scope "<yetki açıklaması>"` çalıştırır,
  ardından Claude'a "pipeline'ı çalıştır" der.
* **B) `incoming/` klasörü (git push):** Keşif botunuz (örn. telefon
  üzerinde çalışan bir araç) `incoming/<ad>.json`'ı şemaya uygun olarak
  (bkz. `incoming/README.md`) repoya push eder. Zamanlanmış görev
  `ingest.py`'yi çalıştırıp bunu alır.

Telegram **giriş kanalı değildir** — yalnızca çıkışta (`dispatch.py
--notify`, tek yönlü `sendDocument`) kullanılır. Sebep: `getUpdates` tek
tüketicili bir API; aynı bot token'ını başka bir taraf (örn. A14'ün
kendi toplayıcı/hakem akışı) da dinlerse mesajları birbirinin elinden
kapar — bu yüzden bu çakışmayı önlemek için Telegram inbound polling
pipeline'dan tamamen çıkarıldı, veri girişi yalnızca `incoming/`
üzerinden.

`ingest.py`:
1. `scope_declaration` yoksa/çok kısaysa → **reddeder**, hiçbir analiz
   başlamaz, `incoming/processed/REJECTED_*` olarak işaretlenir.
2. Geçerliyse → ham veriyi `scripts/bugbounty/out/<hedef>/raw/`'a yazar
   ve `pending_targets` listesine ekler.

Ardından (ister insan "`çalıştır`" dediği an, ister zamanlanmış görev
`ingest.py`'nin ürettiği `pending_targets` listesini gördüğü an) 3 aşama
**art arda, tekrar onay istemeden** çalışır:
- `recon-and-auditor` ham veriyi okur → `stage1_findings.json` yazar.
- `skeptical-triager` her adayı çürütmeye çalışır → `stage2_verdicts.json` yazar.
- `dispatch.py` iki dosyayı birleştirir, yalnızca **confidence ≥ 90 ve
  verdict == PASS** olanları `reports/RAPOR_<hedef>.md`'ye yazar.

Zamanlanmış görev tetiklediğinde, sonuç (`reports/RAPOR_*.md`,
`incoming/processed/*`) bu çalışan branch'e **otomatik commit+push**
edilir, böylece siz canlı bir sohbette olmasanız bile sonuç GitHub'da/
PR'da görünür.

## Elimde olan / olmayan / yapmayacağım (netlik için)

| | Durum |
|---|---|
| Zamanlanmış (cron) görev oluşturmak | ✅ Elimde var, kuruldu |
| Ortamdaki bir API key/token'ı (Telegram, GitHub) kullanmak | ✅ Elimde var |
| Telegram'a bildirim göndermek (`sendDocument`, tek yönlü) | ✅ Elimde var, kuruldu |
| Telegram `getUpdates` ile periyodik mesaj çekmek | ⚠️ Teknik olarak elimde var ama **kasıtlı olarak kullanmıyorum** — tek tüketicili API, A14'ün kendi akışıyla çakışır |
| Herkesin POST atabileceği genel bir webhook URL'i oluşturmak | ❌ Aracım yok (`watch_url` yalnızca Anthropic'in Artifact sistemine özel) |
| HackerOne/GitHub PVR API'sine otomatik rapor gönderimi | 🚫 Bilinçli olarak yapmıyorum (bkz. aşağıdaki bölüm) — araç olsa bile |
| Scope beyanı olmayan veriyi analiz etmek | 🚫 Bilinçli olarak yapmıyorum |

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
incoming/<ad>.json              # Kanal B: bot tarafından push edilen ham veri (işlenince processed/'a taşınır)
incoming/processed/             # işlenmiş (OK_*/REJECTED_*) dosyalar — repoda kalır, denetim izi

scripts/bugbounty/out/<hedef>/
├── raw/                      # scan.sh VEYA ingest.py çıktısı (ham veri, repoya commitlenmez)
├── stage1_findings.json      # Stage 1 çıktısı
└── stage2_verdicts.json      # Stage 2 çıktısı

reports/RAPOR_<hedef>.md      # Stage 3 çıktısı — tek commitlenen nihai sonuç
```

`scripts/bugbounty/out/` tamamen `.gitignore`'da (ham/ara veri); geri
kalan her şey (`incoming/processed/`, `reports/RAPOR_*.md`) bilinçli
olarak repoda tutuluyor — denetim izi için.

## Zamanlanmış görev

`create_trigger` ile saatlik (jitter'lı dakika, sunucu yükünü önlemek
için) çalışan bir görev kuruldu. Her çalıştığında:
1. `python3 scripts/bugbounty/ingest.py` çalıştırılır → `pending_targets` listesi alınır.
2. Her `pending_target` için recon-and-auditor → skeptical-triager → `dispatch.py --notify` sırayla yürütülür.
3. Değişen her şey (`reports/`, `incoming/processed/`) bu branch'e
   commit+push edilir.
4. Yeni bir şey yoksa (`pending_targets` boş, `rejected` boş) hiçbir
   commit yapılmaz, sessizce biter.

## Test

`dispatch.py`, aşağıdaki iki senaryoyla uydurma (sentetik, açıkça test
amaçlı işaretli) fixture verisiyle test edildi:
* 2 adaydan 1'inin eşiği geçtiği, diğerinin reddedildiği bir rapor —
  geçen bulgu tam detayla, reddedilen bulgu yalnızca bir özet tablosunda
  (içeriği olmadan) göründü.
* 0 adayla "temiz" rapor — `[⚪ TEMİZ - GEÇ]` doğru üretildi.
* `--notify` bayrağı, Telegram env değişkenleri yokken hatasız atlandı.

`ingest.py`, uydurma `incoming/*.json` dosyalarıyla test edildi:
* `scope_declaration` dolu olan dosya → kabul edildi, `pending_targets`'a
  girdi, ham veri `out/<hedef>/raw/`'a yazıldı, dosya
  `incoming/processed/OK_*` olarak işaretlendi.
* `scope_declaration` boş olan dosya → reddedildi, hiçbir analiz
  başlamadı, `incoming/processed/REJECTED_*` olarak işaretlendi.

Resmi bir platforma gerçek gönderim **test edilmedi ve edilmeyecek** —
böyle bir testin kendisi gerçek, geri alınamaz bir rapor dosyalaması
anlamına gelirdi.
