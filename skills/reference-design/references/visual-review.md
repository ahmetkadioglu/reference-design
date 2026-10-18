# Görsel ve davranışsal kontrol

Kontrolleri istenen teslimata göre seç. Analiz veya prompt çıktısında uygulama testleri yapıldığını iddia etme.

## Referans belleği kontrolü

- Yeni verilen tüm tasarım referansları kayda geçti mi; analiz durumları ve eksikler doğru mu?
- Aynı URL ikinci kayıt açmadan güncellendi mi ve önceki analiz korunuyor mu?
- Yeni link verilmemiş üretim talebinde bellek gerçekten arandı ve seçilen kayıtların ayrıntıları okundu mu?
- Kaydetme/senkronizasyon başarılı mı; örnek veya test kayıtları gerçek belleğe karıştı mı?
- Yalnızca referans ekleme talebi yanlışlıkla site üretimine dönüştü mü?

## Önce isteğe uyum

- Kullanıcının tema, renk, kapsam, içerik, framework ve bileşen tercihleri uygulanmış mı?
- Kullanıcı A'dan tipografi, B'den kart istediyse tasarım bu rolleri koruyor mu?
- Kendi yorumların açık isteklerin önüne geçmiş mi?
- İncelenmeyen kaynak veya durumlar doğrulanmış gibi sunulmuş mu?

## Teknik inceleme kapsamı

- URL/kod sağlandıysa DOM/HTML, stil kuralları ve ilgili davranış kodu incelenmiş mi; erişilemeyen katmanlar açık mı?
- Önemli özellikler öğe/seçici/dosya ve ilgili kurala bağlanabiliyor mu?
- Tanımlı CSS kuralı ile runtime'da uygulanan değer ayrılmış mı; media query hangi genişlik/durum için geçerli?
- Efektin gerçek katmanı ve mekanizması bulunmuş mu; yalnızca görünüşten CSS tekniği ilan edilmiş mi?
- Kaynak repo olmadan özgün dosya ağacı, framework bileşen mimarisi veya sunucu kodu hakkında kesin iddia var mı?
- Teknik bulgular hedef projenin yapısına uygulanabilir kararlara dönüşmüş mü?

## Sonra görsel karşılaştırma

1. Kompozisyon: hizalar, ana blokların oranları, içerik genişliği ve bölüm ritmi.
2. Tipografi: başlık/gövde ilişkisi, kalınlık, satır uzunluğu ve metin sarması.
3. Yoğunluk: boşluklar, kart içi padding, satır araları ve tekrar eden öğeler.
4. Yüzey: renk rolleri, kenarlıklar, köşeler, gölgeler, doku ve katmanlar.
5. Detay: ikonlar, görsel kırpma, düğme durumları ve istenen hareketler.

İlk üç başlıktaki büyük farkları yalnızca gradient veya gölge ekleyerek kapatmaya çalışma. Referansa benzerliği kullanıcının istediği farklılıkları koruyarak değerlendir.

## Çalışan arayüzde

- Hedef masaüstü ve mobil genişlikte render et; yatay taşma, kesilen içerik ve çakışma var mı bak.
- Navigasyon, menü, düğme, form ve kapsam içindeki durumları gerçekten dene.
- Klavye odağını, etiketleri ve dokunma hedeflerini kontrol et; araç varsa kontrastı ölç.
- Harici servis eksikliğinde demo davranışıyla gerçek başarı mesajını ayır.
- Koddan uyarlanan yerleşim, efekt ve durum mekanizmalarının hedef uygulamada istenen sonucu ürettiğini kontrol et.
- İlgili build/lint veya mevcut proje kontrollerini çalıştır. Görsel kontrol ile teknik kontrolü ayrı raporla.
- Sorun düzelince yalnızca etkilenen kontrolleri tekrarla.

## Teslimat öncesi

- Tamamlanan çıktı, brief veya kod talebinin tamamını karşılıyor mu?
- Kullanılan kaynakların etkisi bir iki somut örnekle açıklanabiliyor mu?
- Çalıştırılmayan test, görülmeyen ekran veya doğrulanmayan font hakkında iddia var mı?
- Varsa temel engel ve onun sonuç üzerindeki etkisi kısa ve açık mı?
