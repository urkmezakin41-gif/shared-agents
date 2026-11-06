# Bug Bounty Raporu — brave-intl_challenge-bypass-server-and-c

**Tarih:** 2026-11-01 22:45 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Brave Software (https://hackerone.com/brave) - SOURCE_CODE wildcard https://github.com/brave/*, https://github.com/brave-intl/* (structured_scope id 943222, max_severity critical). Eksik dosyalar tamamlandi: challenge-bypass-ristretto Rust crate kaynagi (oprf.rs/dleq.rs/voprf.rs/macros.rs/errors.rs) ve challenge-bypass-server (HTTP + Kafka tuketici).
* **Ham veri kaynağı:** `scripts/bugbounty/out/brave-intl_challenge-bypass-server-and-c/raw`
* **Engellenen/erişilemeyen adımlar:** Statik inceleme; Rust crate derlenip test vektorleri elle calistirilmadi (repo icindeki kendi test vektorleri/birim testleri okundu, tekrar uretilmedi)., Postgres/Kafka canli ortam yok.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* DLEQProof/BatchDLEQProof (dleq.rs): standart Chaum-Pedersen tipi NIZK, Ristretto noktalari uzerinde dogru gorunuyor (challenge c=H(X,Y,P,Q,A,B), yanit s=t-ck, doğrulama A=sX+cY, B=sP+cQ, c'==c kontrolu). BatchDLEQProof composite noktalari (M,Z) ChaCha ile seed'lenmis rastgele agirliklarla (Fiat-Shamir benzeri, seed=H(X,Y,{Pi,Qi})) hesapliyor - bu, imzalayan anahtarin TEK bir DLEQProof ile batch icindeki TUM ciftleri ayni anahtarla imzaladigini kanitliyor; kod akisi literatur ile uyumlu.
* oprf.rs RFC9497 hash_to_group_rfc: identity eleman kontrolu var (is_identity() -> InvalidInput hatasi), expand_message_xmd_64 RFC9380'e uygun gorunuyor (tek blok, Z_pad+msg+l_i_b_str+I2OSP(0,1)+DST+dst_len), finalize() (RFC9497 3.3.1 Finalize) uzunluk-onekli (I2OSP len,2) kodlama kullaniyor - duzgun domain-ayirma.
* btd.VerifyTokenRedemption (Go): ACCEPT_LEGACY_TOKENS=false DEGILSE once eski (non-RFC) turetmeyi dener, SADECE ErrInvalidMAC donerse RFC9497 turetmeye duser; identity-preimage hatasi veya baska hata turlerinde geri donmuyor (dogru - yanlis pozitif onleme). Iki turetmeyi de denemenin saldirgana ek bir oracle vermedigi dogrulandi: her ikisi de ayni gizli anahtarla hesaplaniyor, sadece MESAJ/NOKTA turetme fonksiyonu degisiyor; gecerli (preimage,signature,payload) uclusu olmadan hicbir yol basarili olmuyor.
* Sunucu HTTP katmani (server.go, tokens.go, middleware.go): Authenticated Routes grubu SADECE ENV=='production' ise SimpleTokenAuthorizedOnly uyguluyor (bat-go'daki ayni desenle tutarli - staging/dev'de acik, bilinen/kabul edilen davranis, deployment-bagimli dogrulanamaz). isEmpty() kontrolleri (TokenPreimage/Signature nil) tum redeem/issue handler'larinda var. Kafka tuketicisi (signed_token_redeem_handler.go) bos alan kontrolu, public-key eslestirme, VerifyTokenRedemption, CheckRedeemedTokenEquivalence (ID/Binding esitligi ile duplicate/idempotent ayrimi) ve PersistRedemption yaris durumuna karsi ikinci bir equivalence kontrolu ile kapsanmis - saglam gorunuyor.
* Bearer token karsilastirmasi subtle.ConstantTimeCompare kullaniyor ama liste uzerinde dongu + token uzunlugu sizintisi (zaten bat-go'da da not edilmisti, kabul edilen/duplicate bulgu, bu turda yeniden raporlanmadi).

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._