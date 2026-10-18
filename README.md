# Referansla Tasarla · Reference Design

Referans web sitelerini görsel ve teknik olarak analiz eden, bulguları kalıcı bir referans belleğine kaydeden ve sonraki arayüzleri bu birikimden yararlanarak oluşturan agent skill'i.

## Codex / VS Code kurulumu

Codex sohbetine şu isteği gönder:

```text
$skill-installer https://github.com/ahmetkadioglu/reference-design/tree/main/skills/reference-design
```

Özel repo kullanıldığında kurulum ortamına GitHub erişimi de verilmelidir. Kurulumdan sonra `/skills` listesinden `reference-design` skill'ini kontrol et; gerekiyorsa Codex'i yeniden başlat.

Skill dosyaları `skills/reference-design/` altında. Elle kurulumda bu klasörün tamamını kişisel `~/.agents/skills/reference-design/` dizinine kopyala. Windows karşılığı `%USERPROFILE%\.agents\skills\reference-design\` olur. SSH veya WSL ile çalışan Codex için kurulumu agent'ın çalıştığı ortamda yap.

## Kullanım

Referansları belleğe ekle:

```text
$reference-design
Bu siteleri referans belleğine ekle: [URL 1], [URL 2].
İlk sitenin tipografisini, ikincinin kart yüzeylerini beğeniyorum.
```

Daha sonra yeni link vermeden üret:

```text
$reference-design
Referans belleğinden yararlanarak bir randevu platformunun ana sayfasını oluştur.
Açık tema, mavi vurgu, güçlü başlıklar ve hafif pütürlü kartlar istiyorum.
```

Yalnızca tasarım promptu, brief veya analiz istiyorsan bunu açıkça belirt. Yalnızca referans ekleme isteği belleği günceller; site üretimi ayrı bir görevdir.

## İnceleme kapsamı

- Görsel hiyerarşi, tipografi, renk, boşluk, yüzey, doku ve responsive düzen.
- Erişilebilen HTML/DOM, stil dosyaları, computed style, grid/flex, tokenlar ve efekt katmanları.
- CSS/JavaScript etkileşimleri, animasyonlar ve durum değişimleri.
- Kaynak repo verildiğinde ilgili dosya, bileşen ve stil organizasyonu.
- Her bulgu için kaynak, kanıt türü, inceleme tarihi ve erişim sınırları.

Canlı site yalnızca tarayıcıya gönderilen kodu açığa çıkarır. Özgün proje yapısı ve sunucu kodu kaynak erişimi gerektirir. Skill, erişilemeyen ayrıntıları doğrulanmış bulgu gibi sunmaz.

## Referans belleği

Bellek varsayılan olarak kurulu skill'in `references/memory/store.json` dosyasında tutulur ve ilk kayıtta oluşturulur. Referans kayıtları bu dağıtım reposuna dahil edilmez; belleğe yazmak otomatik GitHub gönderimi yapmaz. Aynı URL güncellenir; eski analizler geçmişte korunur. Yeni üretimlerde uygun kayıtlar aranır ve yalnızca seçilenlerin ayrıntıları okunur.

Kurulum konumundan bağımsız tek bir bellek için `REFERENCE_DESIGN_MEMORY_ROOT` ortam değişkenini kalıcı bir dizine ayarlayabilirsin. Birden fazla cihazın aynı birikimi kullanması, o dizinin ayrıca senkronize edilmesini gerektirir. GitHub'dan skill kurulumu otomatik bellek senkronizasyonu kurmaz.

Bellek aracı Python 3 ile çalışır; ek Python paketi gerektirmez:

```bash
python3 skills/reference-design/scripts/reference_memory.py list
python3 skills/reference-design/scripts/reference_memory.py search 'grain kart'
python3 skills/reference-design/scripts/reference_memory.py validate
```

Windows'ta Python kurulumuna göre `python3` yerine `py -3` veya `python` kullan. İsteğe bağlı `--root` parametresi alt komuttan önce gelir.

## Gereksinimler

- Agent Skills uyumlu ve dosya okuyabilen bir agent; bu kurulum akışı Codex içindir.
- Bellek yardımcısı için Python 3 ve yazılabilir kalıcı bir konum.
- Canlı siteleri incelemek için hedef agent'ın ortamında izinli web/tarayıcı ve gerekli DOM/CSS inceleme araçları.

Skill, agent'ın mevcut araçları ve izinleriyle çalışır; tarayıcı veya servis erişimini kendiliğinden sağlamaz.
