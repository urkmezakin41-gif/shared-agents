import ctypes
import time
import sys

# UTF-8 çıktı desteğini yapılandır
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Windows API Virtual Key Kodları
VK_RETURN = 0x0D    # Enter
VK_SCROLL = 0x91    # Scroll Lock
VK_CAPITAL = 0x14   # Caps Lock

# Enter basılacak hedef pencerelerin başlıklarında geçen anahtar kelimeler
# (Büyük/küçük harf duyarsızdır)
TARGET_KEYWORDS = [
    "antigravity", 
    "visual studio code", 
    "vs code", 
    "terminal", 
    "cmd.exe", 
    "powershell", 
    "command prompt",
    "james 0.1",
    "cmd"
]

def get_active_window_title():
    """Şu an en önde/odaklanmış olan pencerenin başlığını döner."""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

def is_key_toggled(vk_code):
    """Kilit tuşunun (Scroll Lock veya Caps Lock) aktif (açık) olup olmadığını döner."""
    # GetKeyState en düşük değerli bit (low-order bit) ile tuşun açık/kapalı durumunu belirtir.
    return bool(ctypes.windll.user32.GetKeyState(vk_code) & 1)

def press_enter():
    """Windows API düzeyinde Enter tuşuna basıp bırakma simülasyonu yapar."""
    # Tuşa bas (Key Down)
    ctypes.windll.user32.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    # Tuşu bırak (Key Up)
    ctypes.windll.user32.keybd_event(VK_RETURN, 0, 2, 0) # 2 = KEYEVENTF_KEYUP

def main():
    print("=" * 60)
    print(" ANTIGRAVITY AUTO-ENTER BOT ".center(60, "═"))
    print("=" * 60)
    print("\n[Açıklama] Bu bot, hedef pencereler aktifken ve kilit tuşu açıkken")
    print("otomatik olarak Enter basar. Ek kütüphane kurulumu gerektirmez.\n")
    
    # Durdurma/başlatma tuş seçimi
    print("Botu açıp kapatmak için kullanılacak tuşu seçin:")
    print("1) Scroll Lock (Önerilen - Eğer klavyenizde varsa)")
    print("2) Caps Lock")
    print("3) Her zaman aktif (Sadece pencere filtresi geçerli olur)")
    
    choice = input("Seçiminiz (1/2/3) [Varsayılan: 1]: ").strip()
    if choice == "2":
        toggle_key = VK_CAPITAL
        key_name = "Caps Lock"
    elif choice == "3":
        toggle_key = None
        key_name = "HER ZAMAN AÇIK"
    else:
        toggle_key = VK_SCROLL
        key_name = "Scroll Lock"
        
    print(f"\n[Ayarlar] Tetikleyici Tuş: {key_name}")
    print(f"[Ayarlar] Hedef Pencereler: {', '.join(TARGET_KEYWORDS)}")
    print("[Ayarlar] Spam Hızı: 1 saniye (Script içinden hızı değiştirebilirsiniz)")
    print("-" * 60)
    print("[ÇALIŞIYOR] Bot başlatıldı. Durdurmak için bu pencerede Ctrl+C yapın.\n")
    
    last_state = None
    
    try:
        while True:
            # 1. Kilit tuş durumunu kontrol et
            is_active = True
            if toggle_key is not None:
                is_active = is_key_toggled(toggle_key)
            
            # 2. Aktif pencere başlığını al
            active_title = get_active_window_title()
            active_title_lower = active_title.lower()
            
            # 3. Aktif pencerenin hedef listesinde olup olmadığını kontrol et
            window_matches = any(kw in active_title_lower for kw in TARGET_KEYWORDS)
            
            # Durum değişikliklerini terminale yazdır
            current_state = (is_active, window_matches, active_title)
            if current_state != last_state:
                if not is_active:
                    status_text = f"DURAKLATILDI ({key_name} Kapalı)"
                elif not window_matches:
                    status_text = f"PASİF (Hedef pencere dışı: '{active_title}')"
                else:
                    status_text = f"AKTİF (SPAMLANIYOR - Hedef pencere: '{active_title}')"
                
                print(f"[{time.strftime('%H:%M:%S')}] Durum: {status_text}")
                last_state = current_state
            
            # 4. Şartlar sağlanıyorsa Enter bas
            if is_active and window_matches:
                press_enter()
                
            # Kontrol sıklığı (spam gecikmesi) - 1 saniye
            # Daha hızlı spam için bu değeri düşürebilirsiniz (örn. 0.2)
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\n\n[SİSTEM] Bot sonlandırıldı.")

if __name__ == "__main__":
    main()
