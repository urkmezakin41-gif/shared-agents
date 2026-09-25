# Sovereign V2 Agents Collection

Yapay zeka kodlama ajanlarını (Antigravity, VS Code, Claude Code vb.) gözetimsiz
çalıştırırken işi akıcı tutan küçük yardımcı ajanlar. Hepsi tek dosyadır ve ek
Python kütüphanesi gerektirmez.

| Ajan | Dosya | Platform | Görev |
|------|-------|----------|-------|
| Auto-Enter Bot | `auto_enter_bot.py` | Windows | Hedef pencere öndeyken otomatik Enter basar |
| Linux Watcher | `linux_watcher.py` | Linux | Süreçleri, çalışma alanını ve sistem kaynaklarını izler, takılmayı bildirir |

## Auto-Enter Bot (Windows)

```bash
python auto_enter_bot.py
```

- Windows API (`ctypes`) ile aktif pencere başlığını okur ve Enter gönderir.
- Tetikleyici: Scroll Lock (önerilen), Caps Lock veya her zaman açık.
- Hedef pencere anahtar kelimeleri dosyanın başındaki `TARGET_KEYWORDS` listesindedir.

## Linux Watcher (Linux)

```bash
python3 linux_watcher.py                                 # bulunduğun dizini izle
python3 linux_watcher.py --path ~/proje --stall 15       # 15 dk değişiklik yoksa uyar
python3 linux_watcher.py --process claude --process code
python3 linux_watcher.py --on-stall 'notify-send "Ajan takıldı"' --log watcher.log
python3 linux_watcher.py --once                          # tek seferlik rapor
```

- **Süreçler:** `/proc` üzerinden izlenen süreç adlarının başlayıp kapandığını bildirir.
- **Çalışma alanı:** Dizindeki eklenen/silinen/değişen dosyaları raporlar; `--stall` dakikası boyunca hareket yoksa `TAKILDI` uyarısı verir.
- **Sistem:** Yük ortalaması, bellek ve disk doluluğunu dakikada bir yazar; eşik aşımında uyarır.
- `--on-stall`, `--on-change`, `--on-process-exit` ile olaylara kabuk komutu bağlanabilir.
- `--duration` ile belirli bir süre sonra kendiliğinden kapanır; `--quiet-files` ile dosya adları yerine yalnızca sayılar yazılır.

## Güvenlik notu

Auto-Enter Bot hedef pencereye gerçekten tuş gönderir. Hedef listesini daraltın ve
tetikleyici kilit tuşunu kapalı tutarak istemediğiniz anlarda botu duraklatın.
Linux Watcher yalnızca okur ve raporlar; sisteme müdahale etmez (kendi verdiğiniz
`--on-*` komutları hariç).
