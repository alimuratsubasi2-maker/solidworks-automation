# SolidWorks Otomasyonu (Python + COM API)

Python (`pywin32`) ile **SolidWorks API**'sini sürerek parça çizimi, montaj, kesit, ölçülendirme ve teknik resim üretimini otomatikleştiren araç seti. Örnek proje: **V6 motor** (blok, piston, krank, supap vb. parçalar ve montaj).

## Neler yapıyor?
- Eskizden parçaya: silindir, döndürme (revolve), kesme (cut), tarama (sweep)
- Parçaları montaja yerleştirme, çakışma (interference) testi
- Teknik resim, kesit ve ölçü çıkarma (DimXpert), tablo/önizleme üretimi
- Toplu görüntü alma ve model denetimi

## Yapı
```
scripts/swlib.py     SolidWorks bağlantısı ve ortak yardımcılar (mm → m dönüşümü)
scripts/asmlib.py    montaj yardımcıları
scripts/*_test.py    özellik denemeleri (revolve, cut, kesit, ölçü ...)
scripts/tr_*.py      teknik resim üretim hattı
V6_Motor_onizleme.png  örnek çıktı
```

## Gereksinimler
Windows, SolidWorks 2026 (lisanslı), Python 3.11+, `pip install pywin32`.

> Şablon yolu `swlib.py` içindeki `TEMPLATE` değişkenidir; kendi kurulumuna göre değiştir.

**Teknolojiler:** Python · COM/pywin32 · SolidWorks API