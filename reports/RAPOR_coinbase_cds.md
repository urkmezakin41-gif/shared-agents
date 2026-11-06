# Bug Bounty Raporu — coinbase_cds

**Tarih:** 2026-11-02 11:40 UTC
**Pipeline:** recon-and-auditor → skeptical-triager → report-dispatcher
**Gönderim eşiği:** verdict == PASS (Claude Karar?)

## 📦 0. Yetki/Scope Kaydı
* **Beyan edilen yetki:** HackerOne Official Program: Coinbase (https://hackerone.com/coinbase) - SOURCE_CODE wildcard https://github.com/coinbase/* (structured_scope id 1028888, max_severity critical). Blok varliga UYUYOR (coinbase/cds, Coinbase Design System - UI komponent kutuphanesi + gelistirici araclari).
* **Ham veri kaynağı:** `scripts/bugbounty/out/coinbase_cds/raw`
* **Engellenen/erişilemeyen adımlar:** Bu turda gelen dosyalarin ezici cogunlugu (storybook/expo-app/vite-app ornekleri, codegen, docusaurus-plugin-docgen) STATIK UI/build-time araclari - canli bir sunucu/API/kimlik dogrulama yuzeyi icermiyor.

### 📓 Analist Notları (bulgu değil, ama kayda değer)
_Bu gözlemler Stage 2'nin ≥90 eşiğine hiç girmedi — somut kanıt eksikliği nedeniyle bilinçli olarak bulgu olarak sunulmadı. Şeffaflık için burada tutuluyor; bir sonraki veri çekiminde ek kaynak kodla yeniden değerlendirilebilir._
* .claude/workflows/code-connect-refresh.js: bu bir Claude Code 'Workflow' script'i (export const meta={...} formatinda), icinde SABIT bir yerel yol var (PROJECT_ROOT = '/Users/erichkuerschner/workspace/cds-public') - bu acikca bir GELISTIRICININ KENDI makinesinde calistirdigi KISISEL otomasyon script'i, repoya (muhtemelen kazara veya referans icin) commit edilmis. CI/production'da calismiyor (sabit yerel path), gizli anahtar/token icermiyor (grep ile dogrulandi), disaridan tetiklenebilir degil. Guvenlik acisindan ONEMSIZ ama bir bilgi ifsasi notu: gelistiricinin yerel kullanici adi/dizin yapisi (zaten zararsiz).
* .agents/skills/skill-creator/scripts/*.py (package_skill.py, run_eval.py, improve_description.py, run_loop.py, vb.): bunlar Claude Code 'skill' gelistirme/test/paketleme icin YEREL CLI araclari (bir gelistiricinin kendi terminalinde calistirdigi). subprocess cagrilari LISTE formunda (shell=True YOK) - shell injection riski yok. package_skill.py zipfile.write ile ZIP OLUSTURUYOR (extract degil) - zip-slip bu yonde uygulanamaz. Hicbiri disaridan erisilebilir bir HTTP endpoint'i degil.
* docgenParser.ts, analyze-bundle.ts, generateIconSvgMap.ts gibi codegen/build script'lerinde readFileSync/execSync/eval/dinamik RegExp kullanim deseni bulunamadi (grep ile tarandi).
* Genel degerlendirme: bu teslimat bir TASARIM SISTEMI (statik React/RN bilesenleri + build/gelistirici araclari); HackerOne'in 'kritik' siniflandirmasina girecek bir kod-calistirma/veri-sizdirma/yetkilendirme-atlama yuzeyi bu dosyalarda gorulmedi. Depo icinde gercek bir saldiri yuzeyi varsa (orn. yayinlanan bir npm paketinin supply-chain riski, ya da CI/CD secrets'ina erisen bir .github/workflows dosyasi), bu turda GELMEDI.

## 📊 1. HIZLI TRİYAJ KARARI
* **Durum:** `[⚪ TEMİZ - GEÇ]`
* **Not:** Stage 1, 0 aday bulgu üretti; bunlardan hiçbiri Stage 2'nin ≥0 confidence eşiğini geçemedi.

---
_Bu rapor `scripts/bugbounty/dispatch.py` tarafından otomatik üretildi. Hiçbir bulgu GitHub Private Vulnerability Reporting API'sine veya HackerOne API'sine otomatik olarak gönderilmedi — gönderim her zaman insan onayı ve elle yapıştırma gerektirir._