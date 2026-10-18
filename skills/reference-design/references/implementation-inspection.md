# Frontend ve kaynak kod incelemesi

URL veya kod verilen görevlerde görsel analize ek olarak bu akışı uygula. İncelemeyi kullanıcının önemsediği sayfa, bileşen ve efektlerle sınırla; ilgisiz bütün bundle'ları okumaya çalışma.

## Erişim katmanlarını ayır

| Elde olan kaynak | Çıkarılabilecek bilgi | Kesinleştirilemeyecek bilgi |
| --- | --- | --- |
| Ekran görüntüsü | Görsel oranlar, yüzey, hiyerarşi; yaklaşık değerler | Özgün CSS, DOM, JS, hover, klasör ağacı |
| HTML / render edilmiş DOM | Eleman ağacı, semantik, sınıflar, tekrarlanan yapılar | Özgün framework bileşen sınırları, kaynak klasörleri |
| CSS / computed style | Tanımlı kurallar; runtime erişiminde belirli öğenin uygulanmış değerleri | Kullanılmayan bir kuralın gerçekten etkili olduğu |
| Tarayıcıya gönderilen JS | Erişilebilen davranış kodu ve bazı teknoloji izleri | Minify edilmiş koddan bütün özgün mimari; sunucu kodu |
| Verilen veya açık kaynak repo | Gerçek dosyalar, bileşenler, tokenlar, durum mantığı ve bağımlılık bildirimleri | Yayındaki sürümle eşitliği doğrulanmayan kaynakların canlı davranışı |

Ortamın araç, tarayıcı ve oturum kurallarına uy. DOM değerlendirme veya ağ kaynaklarına erişim desteklenmiyorsa mevcut izinli araçları kullan; desteklenmeyen DevTools yeteneklerini varmış gibi varsayma. Yalnızca erişilebilir sayfaları, bağlı kaynakları ve verilen/erişilebilir repoyu incele.

## 1. İlgili kodu bul

- Sayfanın ilk HTML'i ile JS sonrası render edilmiş DOM'u ayır. Boş bir uygulama kabuğunu tüm sayfanın kodu sanma.
- İlgili DOM öğelerini, üst kapsayıcıları ve bağlanan stil/script kaynaklarını belirle. Erişilebilir CSS/JS dosyalarında ilgili seçici, sınıf, değişken veya olay üzerinden ara.
- Araçlar izin verdiğinde salt okunur DOM ve computed style incelemesi yap; mevcut browser skill'inin izin verdiği API'lere uy. Accessibility snapshot'ını tam DOM/CSS incelemesi sayma.
- Verilen repo/dosyalarda önce proje talimatlarını oku. İlgili bileşen, stiller, tema/token dosyaları, bağımlılık bildirimleri ve çağrı/ithalat ilişkilerini takip et.
- Kaynak haritası doğrudan bağlı, erişilebilir ve ortam kuralları izin veriyorsa ilgili orijinal kaynağı incelemek için kullan. Özgün kaynak elde edilemiyorsa derlenmiş kod seviyesinde kaldığını belirt.

## 2. Yerleşim ve düzen mantığını çöz

- Ana kapsayıcı genişliğini, max-width/width ilişkisini, margin/padding, gap ve hizalamayı çıkar.
- Grid/flex kurallarını ve üst-alt eleman ilişkisini belirle: kolon tanımı, minmax/auto-fit, flex-basis/grow/shrink, order, wrap ve içerik büyüdüğündeki davranış.
- Position, overflow, sticky, transform, z-index ve yeni stacking context oluşturan özelliklerin katman düzenine etkisini incele.
- CSS custom property'lerini, tema kapsamlarını, tekrar eden tokenları ve bunların bileşenlere nasıl uygulandığını bul.
- Media/container query kırılımlarını ve değişen kuralları kaydet. Kaynaktan bulunan breakpoint'i, gerçekten test edilen viewport'tan ayır; kırılım çevresindeki render davranışını imkân varsa kontrol et.
- Kaynak repo varsa klasörlerin sorumluluklarını, ortak bileşenleri, varyant API'sini, stil kapsülleme yöntemini ve tekrarlanan kalıpları ilgili dosyalarla açıkla. Birkaç DOM tekrarından özgün dosya ağacı oluşturma.

## 3. Efektin hangi katmanda üretildiğini bul

- Font ailesi/ağırlığı/boyutu, line-height, letter-spacing, font-face ve mevcutsa gerçekten kullanılan font bilgilerini incele. Yalnızca ilan edilmiş font stack'ini yüklenen fontun kanıtı sayma.
- Renk, border, radius ve box-shadow değerlerini ilgili öğe ve durumda kaydet. Kaskad, override ve tema değişkeninin çözülmüş sonucunu kontrol et.
- Gradient, arka plan görseli, SVG filter, texture asset, canvas veya CSS filtresi seçeneklerinden hangisinin kanıtlandığını araştır.
- ::before/::after katmanlarını, opacity, mix-blend-mode, mask, filter, backdrop-filter ve isolation ilişkisini incele.
- Grain için örneğin SVG feTurbulence, doku görseli veya canvas üretimi gibi gerçek kaynağı ara; görünen pütürü tek başına belirli bir teknik diye adlandırma.
- Blur'un arka planı mı öğenin kendisini mi etkilediğini ayır. Verilen tek bir blur kuralından tüm yüzeyi glassmorphism diye etiketleme.

## 4. Etkileşim ve hareket mantığını izle

- Hover/focus/active/açık-kapalı durumunun CSS pseudo-class, sınıf, data/aria attribute veya JS state ile nasıl değiştiğini incele.
- Transition/keyframe hedeflerini, süre/delay/easing değerlerini ve tetikleyiciyi bul. Runtime kontrolü mümkünse davranışı gör; salt kod bulgusunu çalışırken doğrulanmış diye sunma.
- Menü, sekme veya diyalog için tetikleyici → durum değişimi → DOM/sınıf/attribute değişimi → görsel sonuç bağını takip et.
- Scroll tabanlı etki varsa ilgili observer/listener/animasyon bağını araştır. Tek başına script dosya adından kullanılan mekanizmayı ilan etme.
- Framework/animasyon kütüphanesini bağımlılık, ithalat veya açık runtime işaretiyle destekle; sınıf adı ve yüzeysel benzerliği kanıt sayma. Kaynak repo yoksa mimari çıkarımının sınırını belirt.

## 5. Bulguyu uygulanabilir karara dönüştür

Kısa bir çalışma kaydı tut; her görevde uzun rapor üretmek gerekmez:

| Özellik | Kanıt | Mekanizma | Hedef projeye uyarlama |
| --- | --- | --- | --- |
| Kart düzeni | Stil dosyasındaki .cards ve media query | Masaüstünde grid, belirli kırılımda tek sütun | Mevcut CardList bileşenine aynı düzen ilkesini uygula |
| Pütürlü yüzey | .card::before ve bağlı texture asset | Düşük opaklıklı ayrı yüzey katmanı | Metin üstünde okunabilirliği koruyan dekoratif katman kur |
| Menü | Buton handler'ı ve aria-expanded | Duruma bağlı panel açılması | Projenin mevcut state ve erişilebilir menü düzenine uyarla |

Kanıt yanında dosya/URL ve seçici/fonksiyon belirt; varsa satır veya incelenen runtime durumunu ekle. İsim ve sayıları gerçekten gördüğün kaynaktan kullan. Verilmeyen hedef tokenları öneri olarak etiketle.

Orijinal implementasyon ile seçtiğin hedef implementasyonu ayır. Kullanıcının promptu ve mevcut proje mimarisi doğrultusunda mekanizmayı uyarla; referansın framework'ünü otomatik zorunluluk yapma.

## Tamamlama ölçütü

- İlgili görünümün hangi DOM/yerleşim, stil/katman ve etkileşim mantığıyla oluştuğu açıklanabiliyor.
- Kanıtlanan en önemli özellikler somut kaynağa bağlanabiliyor.
- Teknik erişim eksikleri ve runtime'da doğrulanmayan bulgular açık.
- Kaynak repo verilmişse ilgili bileşen ve dosya düzeni incelenmiş; verilmemişse bu mimari uydurulmamış.
- Uygulama kararı hem kullanıcı promptunu hem hedef projenin yapısını koruyor.
