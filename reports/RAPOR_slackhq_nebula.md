# Bug Bounty Raporu — slackhq_nebula

**Tarih:** 2026-11-01 07:25 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** confidence >= 90 ve verdict == PASS

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Slack (https://hackerone.com/slack) — Exact Matching SOURCE_CODE Asset Identifier: https://github.com/slackhq/nebula (eligible_for_bounty: true, max_severity: critical). Program notu (onceki gonderiden): yalnizca Critical kabul ediliyor.
* **Ham veri kaynağı:** `scripts/bugbounty/out/slackhq_nebula/raw`
* **Engellenen/erişilemeyen adımlar:** Program sayfasi bu ortamdan dogrulanamadi (hackerone.com agda engelli); scope iddiasi gonderimdeki metne dayaniyor. Yalnizca halka acik kaynak kodun statik incelemesi., 10-06 ve 10-09 gonderimleri BIREBIR ayni (ayni SHA-256); tek hedef olarak islendi. firewall.go bu pakette onceki turda denetlenen surumle BIREBIR ayni (0 satir fark), yeniden bulgu uretilmedi., Saglanmayan dosyalar: ConnectionState.Decrypt/VerifyRelay (tekrar-oynatma penceresi ve AEAD dogrulamasi), header paketi, iputil.IPv6FindUpperProtocol/CreateRejectPacket, handshake_manager/handshake_ix, overlay/batch ve overlay/tio (GRO/TSO birlestirme), cert paketi. Critical seviyesindeki tipik hatalar (handshake, sertifika dogrulama, replay penceresi, birlestirme) BU DOSYALARDA ARANAMADI.

### Ödül Dışı Olarak Atlanan Konular
* [ÖDÜL DEĞERİ YOK - ATLANDI] recv_error ile tunel kapatma: handleRecvError kimlik dogrulamasiz; hostinfo.GetRemote() gecersizse (yalnizca relay uzerinden kurulu tunel) kaynak adres kontrolu atlanip closeTunnel cagriliyor. Saldirgan 32-bit rastgele indeksi bilmeli ve accept_recv_error ayari buna izin vermeli. En kotu durum gecici DoS (tunel yeniden kurulur) — Critical esigine girmez, tasarim geregi kimliksiz mesaj tipi.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* readOutsidePackets: header parse, surum, alt-tip dogrulamasi, 'cift sifrelenmis paket' reddi (UDP kaynagi kendi vpn aginda ise), bilinmeyen index'te yalnizca (relay degilse) recv_error; AEAD dogrulama BASARILI olmadan roaming/connectionManager/firewall adimina gecilmiyor.
* handleOutsideRelayPacket: signedPayload dilimi onceki 'len(packet) < header.Len + Overhead' kontrolu sayesinde sinir icinde. ForwardingType'ta yerinde yeniden insa: yeni AEAD etiketi eskisinin yerine yaziliyor — her iki sifre (AES-GCM/ChaCha20-Poly1305) 16 bayt etiket oldugu icin boyut uyumlu. TerminalType'ta readOutsidePackets ozyinelemeli cagriliyor; ozyineleme derinligi siniri bu dosyada gorunmuyor — ic ice relay paketi uretilebilirligi DOGRULANMADI (kimligi dogrulanmis peer gerektirir), sadece gozlem.
* newPacket/parseV4/parseV6: tum okumalarin oncesinde uzunluk kontrolu var (ihl>=20, ihl+4 / ihl+6 minLen). Ilk-olmayan parcalar port okumuyor, firewall'a Fragment=true olarak gidiyor; 'tiny fragment' (ilk parca portlari kapsamiyor) minLen ile reddediliyor. Parcali paketlere izin ancak 'port: fragment/any' kurali ile (belgelenmis tasarim).
* handleOutsideMessagePacket: kaynak adres sertifikayla eslesmezse (Firewall.Drop) ve kural yoksa paket dusuyor; yalnizca firewall'dan gecen paket TUN batch'ine commit ediliyor.
* consumeInsidePacket / sendMessageNow: handshake sirasinda onbellege alinan paketler gonderim aninda TEKRAR outbound firewall'dan geciriliyor (onbellek firewall'u atlatmiyor). sendInsideEncrypt sayaci Add(1) ile artiriyor, NextMessageCounter()'daki tukenme kontrolunu kullanmiyor — tutarsizlik gozlemi; 2^64'e yakin sayac gerektirdigi icin istismar edilebilir degil.
* SONUC: inside.go ve outside.go'da, 'yalnizca Critical' esigini gececek somut kanitli bir bulgu YOK. En kritik alanlar (replay penceresi, handshake, cert dogrulama, GRO birlestirme) bu pakette bulunmadigindan denetim bu alanlarda YAPILAMADI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥90 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._