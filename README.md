# InventoryFlow Backend

InventoryFlow backend, şirket içi stok, tedarikçi, mal kabul ve talep süreçlerini yöneten Django REST Framework API projesidir.

## Kullanılan Teknolojiler

- Python
- Django
- Django REST Framework
- PostgreSQL
- django-filter
- Token Authentication
- Docker

## Ana Modüller

- `core`: BaseModel, BaseSerializer, BaseViewSet, permission yardımcıları
- `accounts`: kullanıcı profili, roller ve admin kullanıcı yönetimi
- `catalog`: kategori, tedarikçi, ürün ve ürün-tedarikçi ilişkileri
- `receiving`: mal kabul ve stok girişi
- `requisitions`: birim talepleri ve stoktan teslim akışı
- `stock`: stok hareketleri
- `orders`: öğrenme amaçlı sipariş modeli ve endpointleri

## Rol Yapısı

- `admin`: tüm sistemi yönetir, kullanıcı ekleyebilir.
- `operations`: idari işler/personel rolüdür, stok ve tedarik süreçlerini yönetir.
- `department`: birim kullanıcısıdır, sadece kendi birimi adına talep açar ve taleplerini takip eder.

## Temel API Akışı

1. Birim kullanıcısı `/api/stock-requests/` endpointinden talep açar.
2. Ürün kartı yoksa talep yine oluşturulabilir.
3. Admin/idari işler teslim etmeyi denerse ürün kartı veya stok eksikse talep `purchase_needed` olur.
4. Mal kabul ile stok girişi yapılır.
5. Ürün kartı olmayan talep kalemi `link-product` action ile ürün kartına bağlanır.
6. Stok yeterliyse `fulfill` action ile teslim edilir.
7. Ürün stoğu düşer ve `StockMovement` kaydı oluşur.

## Kurulum

Sanal ortam oluştur:

```bash
python -m venv .venv
source .venv/bin/activate
```

Paketleri kur:

```bash
pip install -r requirements.txt
```

`.env` dosyası oluştur:

```bash
cp .env.example .env
```

Migration çalıştır:

```bash
python manage.py migrate
```

Sunucuyu başlat:

```bash
python manage.py runserver
```

API adresi:

```text
http://127.0.0.1:8000/api/
```

## Docker ile Çalıştırma

Backend ve PostgreSQL birlikte çalışır:

```bash
docker compose up --build
```

Migration çalıştır:

```bash
docker compose exec api python manage.py migrate
```

Admin kullanıcı oluştur:

```bash
docker compose exec api python manage.py createsuperuser
```

## Testler

```bash
python manage.py test
```

Özellikle `requisitions/tests.py`, ürün kartı olmayan talep, ürün kartına bağlama ve stoktan teslim akışını test eder.

## Önemli Endpointler

- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`
- `GET/POST /api/products/`
- `GET/POST /api/suppliers/`
- `GET/POST /api/goods-receipts/`
- `GET/POST /api/stock-requests/`
- `POST /api/stock-requests/{id}/fulfill/`
- `POST /api/stock-requests/{id}/items/{item_id}/link-product/`
- `GET /api/stock-movements/`

## Git Notu

Bu repo sadece backend kodlarını içerir. Frontend ayrı repo olarak yönetilir.
