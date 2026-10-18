# Referans inceleme rehberi

Görevin ölçeğine göre derinlik seç. Tek kart için kartı ve ilgili durumlarını; tam site için ilgili sayfa/bölümleri incele. Kullanıcının özellikle tarif ettiği etkilere öncelik ver.

## İncelenecek özellikler

| Alan | Bakılacak ayrıntılar |
| --- | --- |
| Kompozisyon | İçerik genişliği, sütun oranları, hizalama, asimetri, kenar boşluğu, bölüm ritmi |
| Hiyerarşi | İlk dikkat noktası, başlık/gövde oranı, vurgu, CTA konumu, okuma sırası |
| Tipografi | Serif/sans/mono karakteri, kalınlık, boyut oranı, satır yüksekliği, harf aralığı, satır uzunluğu |
| Renk | Sayfa/yüzey/metin/kenarlık/vurgu rolleri, doygunluk, sıcaklık, kontrast |
| Yüzey | Kart biçimi, köşeler, kontur, gölge yayılımı, yükselti, katman sırası |
| Doku | Grain/noise yoğunluğu ve ölçeği, gradient yönü, transparanlık, blur, parlamalar |
| Bileşen | Navigasyon, düğme, kart, input, etiket, tablo; tutarlı tekrar ve içerik yoğunluğu |
| Görsel dil | Fotoğraf/illüstrasyon yaklaşımı, oran, kırpma, ikon kalınlığı ve boyutu |
| Etkileşim | Gözlenebilen hover, focus, açık/kapalı, aktif, yükleniyor, boş ve hata durumları |
| Hareket | Gözlenen tetikleyici, yön, ritim, hiyerarşiye etkisi; gözlenmeyeni öneri olarak belirt |
| Responsive | Gerçekten incelenen görünümde kolon değişimi, sıra, menü, boşluk ve tipografi |

## Kanıt notu

Her kaynak için yalnızca karar vermeye yarayan notları tut:

```text
Kaynak: URL veya verilen görsel adı
İncelenen: sayfa/bölüm, masaüstü/mobil, gözlenen durumlar
Erişim: görsel / DOM / stil dosyası / computed style / JS / kaynak repo; her birinin durumu
Gözlem: görülen biçim, hiyerarşi, renk ve davranış
Teknik kanıt: öğe/seçici/dosya, ilgili kural veya davranış, uygulandığı görünüm/durum
Kanıt türü: görsel tahmin / kodda beyan / runtime doğrulama / kaynak kod
Yaklaşık tahmin: görüntüden çıkarılan ölçü veya muhtemel teknik
Öneri: hedef ürüne aktarılacak ve uyarlanacak ilke
Kısıt: görülmeyen mobil görünüm, doğrulanamayan font/efekt vb.
```

- Font adını CSS/computed style veya açık kaynak bilgisiyle doğrulamadan kesin söyleme; görsel sınıfını tarif et ve uygun alternatif öner.
- Sadece ekran görüntüsü varsa hover/animasyon ve ekran dışında kalan bölümleri gözlenmiş gibi sunma.
- Renk ve ölçüleri gerçekten örneklemediysen kesin kaynak değeri olarak yazma. Önerilen tokenları yaklaşık gözlemden ayrı göster.
- Ekran görüntüsü CSS tekniğini kanıtlamaz. Örneğin blur izlenimi gerçek backdrop-filter yerine görsel bir arka plandan geliyor olabilir.
- Yeni bir referans eski analizi değiştiriyorsa kanıt notunu ve kararları güncelle.

## Kaynaklardan sentez

Birden fazla referansta gerektiğinde şu küçük tabloyu kullan:

| Tasarım alanı | Kaynak | Görsel/teknik bulgu | Hedef ürüne uyarlama |
| --- | --- | --- | --- |
| Tipografi | A | Büyük başlık, kısa satırlar | Ürünün içeriğiyle belirgin başlık hiyerarşisi |
| Kartlar | B | İnce kontur, hafif gölge | Kullanıcının istediği renk ve köşe sistemiyle yüzeyler |

Kullanıcı kaynakların rollerini belirlediyse tabloyu o rollere göre doldur. Belirlemediyse bütün sitelerin bütün özelliklerini harmanlama; baskın yönü seç ve gerekçesini kısa tut.

## Tasarım kararı kaydı

Uygulama öncesinde aşağıdakileri netleştir; sayıların kaynaktan ölçüm mü kendi önerin mi olduğunu belirt:

- Sayfa ve bileşen kapsamı; ana kullanıcı eylemi.
- Zorunlu kullanıcı tercihleri ve yapılmayacak görsel tercihler.
- Baskın referans ve yardımcı referansların rolleri.
- Anlamsal renk paleti; başlık, gövde ve yardımcı metin hiyerarşisi.
- Genişlik, grid, boşluk, köşe, kenarlık, gölge ve varsa doku değerleri.
- Kanıtlanan DOM/yerleşim, CSS/efekt ve etkileşim mekanizmaları; hedef bileşen/stil düzeni ve uyarlama kararları.
- Gözlenen mobil davranış ile tasarlanan mobil uyarlamanın ayrımı.
- Gerekli durumlar ve kabul ölçütleri.

Büyük projede mevcut dokümantasyon düzenine uygun kayıt tut; küçük görevde kısa çalışma notu yeterlidir. Her iş için otomatik rapor dosyaları üretme.
