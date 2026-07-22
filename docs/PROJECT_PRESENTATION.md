# InventoryFlow Proje Sunum Notlari

Bu dokuman, InventoryFlow projesini proje yoneticisine veya teknik mulakatta kisa ve net anlatmak icin hazirlandi.

## Proje Amaci

InventoryFlow, sirket icindeki stok, tedarikci, mal kabul ve birim talep sureclerini yoneten full-stack bir envanter uygulamasidir.

Sistem su sorulara cevap verir:

- Depoda hangi urunden ne kadar var?
- Hangi tedarikciden hangi urun geldi?
- Hangi birim hangi urunu talep etti?
- Talep stoktan teslim edildi mi, yoksa tedarik mi bekliyor?
- Stok hareketleri nereden olustu?

## Temel Is Akisi

1. Admin veya idari isler sisteme urun karti tanimlar.
2. Tedarikci bilgileri anlasmali firma olarak kaydedilir.
3. Tedarikciden urun geldiginde mal kabul kaydi olusturulur.
4. Mal kabul kaydedilince urun stogu otomatik artar.
5. Birim kullanicisi ihtiyac duydugu urunler icin talep acar.
6. Admin veya idari isler stok uygunsa talebi teslim eder.
7. Stok yoksa talep tedarik bekliyor durumuna duser.
8. Teslim veya mal kabul islemleri stok hareketi olarak kaydedilir.

## Sayfalarin Gorevi

### Dashboard

Sistemin ozet ekranidir. Toplam urun, toplam stok, kritik stok, bekleyen talep, tedarik bekleyen talep ve son hareketler tek ekranda gorulur.

### Urunler

Urun kartlarinin yonetildigi yerdir. Urun karti stok girisi yapmaz; sadece urunun sistemde tanimli olmasini saglar.

### Tedarikciler

Anlasmali firmalarin tutuldugu yerdir. Yeni firma eklenebilir, firma bilgileri guncellenebilir ve pasife alinabilir.

### Mal Kabul

Depoya urun girisinin yapildigi ana ekrandir. Tedarikci, gelen urun, miktar ve birim maliyet girilir. Kayit tamamlandiginda stok artar.

### Talepler

Birim kullanicilarinin urun ihtiyaci actigi ekrandir. Urun sistemde varsa secilir, yoksa "urun listede yok" secenegiyle talep acilir.

### Stok Hareketleri

Mal kabul girisleri ve talep teslim cikislari burada izlenir.

### Kullanicilar

Admin tarafindan kullanici ekleme, duzenleme, pasife alma ve tekrar aktife alma islemleri yapilir.

## Roller

- Admin: Tum sistemi ve kullanicilari yonetir.
- Idari Isler: Urun, tedarikci, mal kabul, talep ve stok sureclerini yonetir.
- Birim Kullanicisi: Talep acar ve talep durumunu takip eder.

## Kullanilan Teknolojiler

### Backend

- Python
- Django
- Django REST Framework
- PostgreSQL
- django-filter
- Token Authentication
- transaction.atomic
- select_related ve prefetch_related
- Unit test yapisi

### Frontend

- Vite
- Vue 3
- Vue Router
- Pinia
- Axios
- Vuetify
- Tailwind CSS
- vue-i18n
- Light, dark ve system theme

### Araclar

- Git
- GitHub
- Docker
- npm
- Python virtual environment

## Teknik Olarak One Cikan Noktalar

- Ortak alanlar icin BaseModel kullanildi.
- Ortak API davranislari icin BaseModelViewSet kullanildi.
- Serializer yapisi ile veriler validate edildi ve JSON formatina cevrildi.
- Permission yapisi ile rollerin hangi islemleri yapabilecegi sinirlandirildi.
- Mal kabul ve talep teslimi gibi kritik islemlerde transaction.atomic kullanildi.
- select_related ve prefetch_related ile gereksiz veritabani sorgulari azaltildi.
- Urun kodu kullanici tarafindan bilinmeyebilir diye backend uzerinden otomatik PRD-0001 formatinda kod uretme endpointi eklendi.

## Demo Sirasi

1. Admin ile giris yap.
2. Dashboard ozetini goster.
3. Tedarikci ekle veya mevcut tedarikciyi duzenle.
4. Urun karti olustur ve Kod olustur butonunu goster.
5. Mal kabulden tedarikci ve urun ara, miktar gir, kaydet.
6. Urun stok miktarinin arttigini goster.
7. Stok hareketleri ekraninda giris hareketini goster.
8. Birim kullanicisi ile talep ac.
9. Admin/idari isler ile talebi teslim et veya tedarik bekliyor akisina dusur.
10. Kullanicilar ekraninda rol ve aktif/pasif mantigini goster.

## Kisa Mulakat Cevabi

InventoryFlow, sirket icindeki stok ve talep sureclerini yoneten bir envanter uygulamasidir. Backend tarafinda Django REST Framework ve PostgreSQL kullandim. Frontend tarafinda Vue 3, Vite, Router, Pinia, Axios, Vuetify ve Tailwind kullandim. Urun karti, tedarikci, mal kabul, talep, stok hareketi ve kullanici yonetimi modulleri var. Stok girisi mal kabulden yapiliyor, talepler stoktan teslim ediliyor veya tedarik bekliyor durumuna aliniyor. Kritik islemlerde transaction.atomic ile veri tutarliligi saglandi.
