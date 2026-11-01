# Bug Bounty Raporu — base_usbwallet

**Tarih:** 2026-11-01 22:45 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/base/* (structured_scope id 1028889, max_severity critical). Blok varliga UYUYOR (base/usbwallet: Ledger/Trezor APDU framing + EIP-712 imzalama, go-ethereum usbwallet'in base fork'u).
* **Ham veri kaynağı:** `scripts/bugbounty/out/base_usbwallet/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; gercek USB donanimi/Ledger-Trezor cihazi yok, calistirilmadi., usb/ alt paketi (karalabe/usb yerine base/usbwallet/usb) vendoring; HID/WebUSB transport katmani ayrintili incelenmedi (upstream, degismemis gorunuyor).

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* ledgerSign/ledgerSignTypedHash, trezorSign/SignTypedHash: upstream go-ethereum usbwallet koduyla esasen ozdes (iyi denetlenmis). SignTx hem Ledger hem Trezor'da donen imzadan sender adresini recover edip beklenen account.Address ile karsilastiriyor ('hardware fault' kontrolu); ancak SignTypedHash/SignedTypedData (EIP-712) yolunda bu sender-recover kontrolu YOK - hem upstream'de hem bu fork'ta boyle. Bu, cihazin yanlis anahtarla imzalamasi durumunda APDU/driver seviyesinde yakalanmiyor; downstream tuketici (task-signing-tool/eip712sign, once incelendi) kendi recoverAddress kontrolunu yapiyor, dolayisiyla bu katmanda tek basina sistemik risk degil.
* usb/ vendoring: karalabe/usb yerine base/usbwallet/usb kullanimina gecis + lisans/AUTHORS dosyalari - guvenlik degil, bagimlilik degisikligi.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 1 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

## 🗑️ Elenen Bulgular (Stage 2 tarafından reddedildi veya eşiğin altında kaldı)

| ID | Confidence | Verdict | Sebep |
|---|---|---|---|
| F1 | 10 | REJECT | HEAD'de yamali; gecmis bir surum guvenlik acigi arsiv notu olarak kaydedildi, aktif rapor degil. |  |

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._