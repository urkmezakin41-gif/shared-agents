#!/usr/bin/env python3
"""
LINUX WATCHER - Sovereign V2 Agents Collection

Yapay zeka ajanlarının (Claude Code, Antigravity, VS Code vb.) çalıştığı bir
Linux makineyi izleyen hafif bir gözcü ajandır. Üç şeyi takip eder:

  1. SÜREÇLER : İzlenen süreç adları çalışıyor mu? (başladı/kapandı bildirimi)
  2. ÇALIŞMA ALANI : İzlenen dizinde dosya değişiyor mu? Uzun süre değişmezse
                     "TAKILDI" uyarısı verir (ajan durmuş olabilir).
  3. SİSTEM : Yük ortalaması, bellek ve disk doluluğu; eşik aşılırsa uyarır.

Ek Python kütüphanesi GEREKMEZ. Sadece /proc ve standart kütüphane kullanılır.

Örnekler:
  python3 linux_watcher.py                          # bulunduğun dizini izle
  python3 linux_watcher.py --path ~/proje --stall 15
  python3 linux_watcher.py --process claude --process code --log watcher.log
  python3 linux_watcher.py --on-stall 'notify-send "Ajan takıldı"'
  python3 linux_watcher.py --once                   # tek seferlik durum raporu
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

# UTF-8 çıktı desteğini yapılandır
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

# Varsayılan olarak izlenen süreç adları (komut adında veya komut satırında geçer)
DEFAULT_PROCESSES = ["claude", "antigravity", "code", "node", "python"]

# Dizin taramasında atlanan klasörler
IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".cache", "dist", "build"}


class Logger:
    """Ekrana ve isteğe bağlı olarak dosyaya zaman damgalı satır yazar."""

    def __init__(self, log_path=None):
        self.log_path = log_path

    def write(self, level, message):
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}"
        print(line)
        if self.log_path:
            try:
                with open(self.log_path, "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            except OSError as exc:
                print(f"[UYARI] Log dosyasına yazılamadı: {exc}")


# ---------------------------------------------------------------------------
# 1. SÜREÇ İZLEME
# ---------------------------------------------------------------------------
def list_processes():
    """/proc üzerinden (pid, komut adı, komut satırı) listesi döner."""
    procs = []
    try:
        pids = [p for p in os.listdir("/proc") if p.isdigit()]
    except OSError:
        return procs
    for pid in pids:
        try:
            with open(f"/proc/{pid}/comm", encoding="utf-8", errors="replace") as fh:
                comm = fh.read().strip()
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                cmdline = fh.read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
        except OSError:
            continue  # süreç bu arada kapanmış olabilir
        procs.append((int(pid), comm, cmdline))
    return procs


def find_processes(keywords):
    """Her anahtar kelime için eşleşen pid listesini döner.

    Gözcünün kendisi, onu başlatan kabuk ve komut satırında bu betiğin adı geçen
    sarmalayıcılar hariç tutulur; yoksa --process argümanları kendi kendini eşler.
    """
    found = {kw: [] for kw in keywords}
    self_pids = {os.getpid(), os.getppid()}
    self_marker = os.path.basename(__file__).lower()
    for pid, comm, cmdline in list_processes():
        if pid in self_pids:
            continue
        haystack = f"{comm} {cmdline}".lower()
        if self_marker in haystack:
            continue
        for kw in keywords:
            if kw in haystack:
                found[kw].append(pid)
    return found


# ---------------------------------------------------------------------------
# 2. ÇALIŞMA ALANI İZLEME
# ---------------------------------------------------------------------------
def snapshot_dir(root, exclude=frozenset(), max_files=50000):
    """Dizindeki dosyaların {yol: (mtime, boyut)} anlık görüntüsünü döner.

    exclude: izlenmeyecek mutlak dosya yolları (örn. gözcünün kendi log dosyası).
    """
    snap = {}
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            if full in exclude:
                continue
            try:
                st = os.stat(full)
            except OSError:
                continue
            snap[full] = (st.st_mtime, st.st_size)
            count += 1
            if count >= max_files:
                return snap
    return snap


def diff_snapshots(old, new):
    """İki anlık görüntü arasındaki (eklenen, silinen, değişen) dosya listelerini döner."""
    added = [p for p in new if p not in old]
    removed = [p for p in old if p not in new]
    changed = [p for p in new if p in old and old[p] != new[p]]
    return added, removed, changed


# ---------------------------------------------------------------------------
# 3. SİSTEM İZLEME
# ---------------------------------------------------------------------------
def read_loadavg():
    try:
        with open("/proc/loadavg", encoding="utf-8") as fh:
            parts = fh.read().split()
        return float(parts[0]), float(parts[1]), float(parts[2])
    except (OSError, ValueError, IndexError):
        return None


def read_memory_percent():
    """Kullanılan bellek yüzdesini döner (MemAvailable tabanlı)."""
    try:
        info = {}
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                key, _, rest = line.partition(":")
                info[key.strip()] = int(rest.split()[0])
        total = info["MemTotal"]
        available = info.get("MemAvailable", info.get("MemFree", 0))
        return 100.0 * (total - available) / total if total else None
    except (OSError, KeyError, ValueError, IndexError):
        return None


def read_disk_percent(path):
    try:
        usage = shutil.disk_usage(path)
        return 100.0 * usage.used / usage.total if usage.total else None
    except OSError:
        return None


def run_hook(command, logger, label):
    """Kullanıcının verdiği kabuk komutunu çalıştırır (örn. notify-send)."""
    if not command:
        return
    logger.write("HOOK", f"{label} komutu çalıştırılıyor: {command}")
    try:
        subprocess.Popen(command, shell=True)
    except OSError as exc:
        logger.write("UYARI", f"{label} komutu başlatılamadı: {exc}")


# ---------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Linux Watcher: süreç, çalışma alanı ve sistem gözcüsü."
    )
    parser.add_argument("--path", default=os.getcwd(), help="İzlenecek dizin (varsayılan: bulunduğun dizin).")
    parser.add_argument(
        "--process",
        action="append",
        default=[],
        help="İzlenecek süreç adı/anahtar kelimesi (birden fazla kullanılabilir). "
        f"Varsayılan: {', '.join(DEFAULT_PROCESSES)}",
    )
    parser.add_argument("--interval", type=float, default=5.0, help="Kontrol aralığı saniye (varsayılan: 5).")
    parser.add_argument("--stall", type=float, default=10.0, help="Bu kadar dakika dosya değişmezse TAKILDI uyarısı (0 = kapalı).")
    parser.add_argument("--mem-limit", type=float, default=90.0, help="Bellek uyarı eşiği yüzde (varsayılan: 90).")
    parser.add_argument("--disk-limit", type=float, default=90.0, help="Disk uyarı eşiği yüzde (varsayılan: 90).")
    parser.add_argument("--log", help="Olayların ekleneceği log dosyası.")
    parser.add_argument("--on-stall", help="TAKILDI durumunda çalıştırılacak kabuk komutu.")
    parser.add_argument("--on-change", help="Dosya değişikliğinde çalıştırılacak kabuk komutu.")
    parser.add_argument("--on-process-exit", help="İzlenen süreç kapanınca çalıştırılacak kabuk komutu.")
    parser.add_argument("--quiet-files", action="store_true", help="Tek tek dosya adlarını yazma, sadece sayıları yaz.")
    parser.add_argument("--duration", type=float, default=0, help="Bu kadar saniye sonra kendiliğinden çık (0 = süresiz).")
    parser.add_argument("--once", action="store_true", help="Tek seferlik durum raporu ver ve çık.")
    return parser.parse_args()


def print_system_report(logger, path, mem_limit, disk_limit, state):
    """Sistem ölçümlerini yazar; eşik aşımlarını sadece durum değişince uyarır."""
    load = read_loadavg()
    mem = read_memory_percent()
    disk = read_disk_percent(path)
    cpu_count = os.cpu_count() or 1

    parts = []
    if load:
        parts.append(f"yük {load[0]:.2f}/{load[1]:.2f}/{load[2]:.2f} ({cpu_count} çekirdek)")
    if mem is not None:
        parts.append(f"bellek %{mem:.0f}")
    if disk is not None:
        parts.append(f"disk %{disk:.0f}")
    logger.write("SİSTEM", " | ".join(parts) if parts else "ölçüm alınamadı")

    mem_high = mem is not None and mem >= mem_limit
    disk_high = disk is not None and disk >= disk_limit
    if mem_high != state.get("mem_high"):
        state["mem_high"] = mem_high
        if mem_high:
            logger.write("UYARI", f"Bellek kullanımı eşiği aştı: %{mem:.0f} >= %{mem_limit:.0f}")
    if disk_high != state.get("disk_high"):
        state["disk_high"] = disk_high
        if disk_high:
            logger.write("UYARI", f"Disk doluluğu eşiği aştı: %{disk:.0f} >= %{disk_limit:.0f}")


def main():
    args = parse_args()
    logger = Logger(args.log)
    root = os.path.abspath(os.path.expanduser(args.path))
    keywords = [k.lower() for k in (args.process or DEFAULT_PROCESSES)]

    print("=" * 60)
    print(" LINUX WATCHER ".center(60, "═"))
    print("=" * 60)
    print("\n[Açıklama] Bu ajan; izlenen süreçleri, çalışma alanındaki dosya")
    print("hareketini ve sistem kaynaklarını takip eder, olayları raporlar.\n")

    if not os.path.isdir(root):
        print(f"[HATA] İzlenecek dizin bulunamadı: {root}")
        sys.exit(1)
    if not os.path.isdir("/proc"):
        print("[UYARI] /proc bulunamadı: süreç ve sistem izleme çalışmayacak (Linux dışı sistem?).")

    print(f"[Ayarlar] Dizin: {root}")
    print(f"[Ayarlar] Süreçler: {', '.join(keywords)}")
    print(f"[Ayarlar] Aralık: {args.interval} sn | Takılma eşiği: {args.stall} dk")
    print(f"[Ayarlar] Bellek eşiği: %{args.mem_limit:.0f} | Disk eşiği: %{args.disk_limit:.0f}")
    if args.log:
        print(f"[Ayarlar] Log dosyası: {args.log}")
    print("-" * 60)

    # İlk durum
    system_state = {}
    proc_state = find_processes(keywords)
    for kw, pids in proc_state.items():
        status = f"ÇALIŞIYOR (pid: {', '.join(map(str, pids[:5]))})" if pids else "YOK"
        logger.write("SÜREÇ", f"'{kw}': {status}")

    # Gözcünün kendi log dosyası izlenen dizinde olsa bile değişiklik sayılmaz
    exclude = frozenset({os.path.abspath(args.log)}) if args.log else frozenset()
    snapshot = snapshot_dir(root, exclude)
    logger.write("DİZİN", f"{len(snapshot)} dosya izleniyor.")
    print_system_report(logger, root, args.mem_limit, args.disk_limit, system_state)

    if args.once:
        return

    print("\n[ÇALIŞIYOR] Gözcü başlatıldı. Durdurmak için Ctrl+C yapın.\n")

    last_activity = time.monotonic()
    stalled = False
    started = time.monotonic()
    last_system_report = time.monotonic()

    try:
        while True:
            time.sleep(args.interval)

            # 1. Süreçler
            current = find_processes(keywords)
            for kw in keywords:
                was_running = bool(proc_state.get(kw))
                now_running = bool(current.get(kw))
                if now_running and not was_running:
                    logger.write("SÜREÇ", f"'{kw}' BAŞLADI (pid: {', '.join(map(str, current[kw][:5]))})")
                elif was_running and not now_running:
                    logger.write("SÜREÇ", f"'{kw}' KAPANDI")
                    run_hook(args.on_process_exit, logger, "on-process-exit")
            proc_state = current

            # 2. Çalışma alanı
            new_snapshot = snapshot_dir(root, exclude)
            added, removed, changed = diff_snapshots(snapshot, new_snapshot)
            if added or removed or changed:
                last_activity = time.monotonic()
                if stalled:
                    logger.write("DİZİN", "Aktivite geri geldi, TAKILDI durumu kalktı.")
                    stalled = False
                logger.write(
                    "DİZİN",
                    f"+{len(added)} eklendi, -{len(removed)} silindi, ~{len(changed)} değişti",
                )
                if not args.quiet_files:
                    for p in (added + changed + removed)[:10]:
                        logger.write("DOSYA", os.path.relpath(p, root))
                run_hook(args.on_change, logger, "on-change")
            snapshot = new_snapshot

            # Takılma kontrolü
            if args.stall > 0 and not stalled:
                idle_minutes = (time.monotonic() - last_activity) / 60.0
                if idle_minutes >= args.stall:
                    stalled = True
                    logger.write("UYARI", f"TAKILDI: {idle_minutes:.0f} dakikadır dosya değişikliği yok.")
                    run_hook(args.on_stall, logger, "on-stall")

            # 3. Sistem (her 60 saniyede bir)
            if time.monotonic() - last_system_report >= 60:
                print_system_report(logger, root, args.mem_limit, args.disk_limit, system_state)
                last_system_report = time.monotonic()

            # Süre sınırı
            if args.duration and (time.monotonic() - started) >= args.duration:
                logger.write("SİSTEM", f"{args.duration} saniye doldu, gözcü kapanıyor.")
                break

    except KeyboardInterrupt:
        print("\n\n[SİSTEM] Gözcü sonlandırıldı.")


if __name__ == "__main__":
    main()
