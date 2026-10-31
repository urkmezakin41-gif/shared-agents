# `incoming/` — Keşif Botu Veri Teslim Noktası

Keşif botunuz (veya herhangi bir araç) buraya ham keşif verisini JSON
olarak **push** eder. Zamanlanmış görev bu klasörü periyodik olarak
kontrol eder (`scripts/bugbounty/ingest.py`); yeni, geçerli bir dosya
bulursa pipeline'ı (Stage 1→2→3) otomatik tetikler.

## Dosya formatı

Dosya adı: `<herhangi_bir_isim>.json` (çakışmayı önlemek için zaman damgası
önerilir, örn. `2026-10-31T23-00-00_example.com.json`).

```json
{
  "target": "example.com",
  "scope_declaration": "ZORUNLU — boşsa veya yoksa dosya İŞLENMEZ, 'rejected' olarak işaretlenir. Kendi mülkiyeti / program adı-URL'si / sözleşme referansı gibi somut bir yetki açıklaması olmalı.",
  "raw": {
    "crtsh_subdomains": ["sub1.example.com", "sub2.example.com"],
    "cname_records": {"staging.example.com": "something.s3.amazonaws.com"},
    "js_endpoints": [
      {"source_url": "https://example.com/app.js", "matches": ["/api/v1/admin/export"]}
    ],
    "homepage_html_excerpt": "<opsiyonel, ilgili kısım>",
    "github_commit_diff": "<opsiyonel, unified diff metni>"
  }
}
```

* `target` ve `scope_declaration` zorunlu; `scope_declaration` boşsa veya
  5 karakterden kısaysa dosya reddedilir.
* `raw` içindeki alanların hepsi opsiyonel ama en az biri dolu olmalı
  (hepsi boşsa analiz edilecek bir şey yoktur, dosya "empty" olarak
  işaretlenir, pipeline tetiklenmez).
* İşlenen dosyalar `incoming/processed/` altına taşınır (başarıyla
  işlendiyse `OK_` öneki, reddedildiyse `REJECTED_<sebep>_` öneki ile).

## Alternatif kanal: Telegram

`TELEGRAM_BOT_TOKEN` ortam değişkeni ayarlıysa, aynı JSON şemasını bir
belge (document) olarak doğrudan o Telegram botuna gönderebilirsiniz;
`ingest.py` periyodik olarak `getUpdates` ile kontrol edip indirir ve
aynı şekilde işler. `incoming/` klasörüne push etmekle işlevsel olarak
aynıdır, sadece teslim kanalı farklıdır.
