# 🎓 SQL EĞİTİMİ UYGULAMA REHBERİ (OKUL VERİTABANI)

Bu rehber, **okul.db** SQLite veritabanı üzerinden temelden ileri seviyeye SQL öğrenmek ve öğretmek için hazırlanmış pratik sorgu senaryolarını içerir.

---

## 🗄️ Veritabanı Tabloları & İlişki Şeması (ERD)

- **`ogrenciler`**: 200 Öğrenci (id, okul_no, ad, soyad, cinsiyet, sinif, sube, boy_cm, kilo_kg)
- **`yoklama`**: 18.000 Kayıt (id, ogrenci_id, tarih, durum: 'Geldi', 'Gelmedi', 'Izinli')
- **`ogretmenler`**: 16 Branş Öğretmeni (id, ad, soyad, brans, cinsiyet, telefon, eposta)
- **`siniflar`**: 16 Şube (id, sinif_seviye, sube, sinif_adi, derslik, rehber_ogretmen_id)
- **`dersler`**: 12 Temel Müfredat Dersi (id, ders_kodu, ders_adi, haftalik_saat, kategori)
- **`haftalik_ders_programi`**: 560 Ders Saati (id, sinif_id, ders_id, ogretmen_id, gun, ders_saati, derslik)

---

## ⚡ 1. INDEX (Dizin) Analizi ve Performans Eğitimi

Index'ler, tablolarda milyonlarca satır varken sorguların milisaniyeler içinde dönmesini sağlayan arama ağaçlarıdır (B-Tree).

### A) Mevcut Dizinleri Görme
```sql
SELECT type, name, tbl_name, sql 
FROM sqlite_master 
WHERE type = 'index';
```

### B) EXPLAIN QUERY PLAN ile İndeks Kullanımını Test Etme
**İndeksli Arama (Hızlı - B-Tree Arama):**
```sql
EXPLAIN QUERY PLAN
SELECT * FROM ogrenciler WHERE sinif = '8' AND sube = 'A';
-- Çıktı: SEARCH TABLE ogrenciler USING INDEX idx_ogrenciler_sinif_sube
```

**İndekssiz Arama (Yavaş - Tam Tablo Taraması):**
```sql
EXPLAIN QUERY PLAN
SELECT * FROM ogrenciler WHERE boy_cm > 165;
-- Çıktı: SCAN TABLE ogrenciler (Tüm satırlar tek tek okunur)
```

---

## 🧩 2. Temelden İleriye SQL Alıştırmaları

### Seviye 1: Temel Filtreleme (WHERE, ORDER BY, LIMIT)
**Soru 1:** 8. sınıfa giden ve boyu 160 cm'den uzun kız öğrencileri bulun:
```sql
SELECT okul_no, ad, soyad, sinif || '/' || sube AS sinif_sube, boy_cm, kilo_kg 
FROM ogrenciler 
WHERE sinif = '8' AND cinsiyet = 'Kız' AND boy_cm > 160.0
ORDER BY boy_cm DESC;
```

---

### Seviye 2: Gruplama ve Toplama Fonksiyonları (GROUP BY, HAVING)
**Soru 2:** Her sınıf düzeyindeki (5, 6, 7, 8) öğrenci sayısı, ortalama boy ve kilo istatistikleri:
```sql
SELECT 
    sinif,
    COUNT(*) AS ogrenci_sayisi,
    ROUND(AVG(boy_cm), 1) AS ortalama_boy,
    ROUND(AVG(kilo_kg), 1) AS ortalama_kilo,
    MIN(boy_cm) AS en_kisa_boy,
    MAX(boy_cm) AS en_uzun_boy
FROM ogrenciler
GROUP BY sinif
ORDER BY sinif ASC;
```

**Soru 3:** 90 günde 6 günden fazla devamsızlığı olan öğrencileri bulun (HAVING kullanımı):
```sql
SELECT 
    o.okul_no,
    o.ad,
    o.soyad,
    o.sinif || '/' || o.sube AS sinif,
    COUNT(*) AS devamsizlik_gun_sayisi
FROM ogrenciler o
JOIN yoklama y ON o.id = y.ogrenci_id
WHERE y.durum = 'Gelmedi'
GROUP BY o.id
HAVING COUNT(*) >= 6
ORDER BY devamsizlik_gun_sayisi DESC;
```

---

### Seviye 3: Çoklu Tablo Birleştirme (JOIN) & Ders Programı
**Soru 4:** "5/A" sınıfının Pazartesi günkü tam ders programı ve derse giren öğretmenlerin listesi:
```sql
SELECT 
    p.gun,
    p.ders_saati || '. Ders' AS saat,
    d.ders_adi,
    d.kategori,
    ogr.ad || ' ' || ogr.soyad AS ders_ogretmeni,
    ogr.brans,
    p.derslik
FROM haftalik_ders_programi p
JOIN siniflar s ON p.sinif_id = s.id
JOIN dersler d ON p.ders_id = d.id
JOIN ogretmenler ogr ON p.ogretmen_id = ogr.id
WHERE s.sinif_adi = '5/A' AND p.gun = 'Pazartesi'
ORDER BY p.ders_saati ASC;
```

**Soru 5:** Matematik öğretmeni "Kemal Yıldız"ın haftalık ders programı (Hangi gün, hangi saatte hangi sınıfta?):
```sql
SELECT 
    p.gun,
    p.ders_saati,
    s.sinif_adi,
    d.ders_adi,
    p.derslik
FROM haftalik_ders_programi p
JOIN ogretmenler ogr ON p.ogretmen_id = ogr.id
JOIN siniflar s ON p.sinif_id = s.id
JOIN dersler d ON p.ders_id = d.id
WHERE ogr.ad = 'Kemal' AND ogr.soyad = 'Yıldız'
ORDER BY 
    CASE p.gun
        WHEN 'Pazartesi' THEN 1
        WHEN 'Salı' THEN 2
        WHEN 'Çarşamba' THEN 3
        WHEN 'Perşembe' THEN 4
        WHEN 'Cuma' THEN 5
    END,
    p.ders_saati ASC;
```

---

### Seviye 4: İleri Seviye (Subquery, CASE WHEN, CTE)
**Soru 6:** Her sınıfın rehber öğretmenini ve o sınıftaki kız/erkek öğrenci oranını pivot yapma:
```sql
SELECT 
    s.sinif_adi,
    s.derslik,
    COALESCE(ogr.ad || ' ' || ogr.soyad, 'Atanmadı') AS rehber_ogretmen,
    ogr.brans,
    COUNT(o.id) AS toplam_mevcut,
    SUM(CASE WHEN o.cinsiyet = 'Erkek' THEN 1 ELSE 0 END) AS erkek_sayisi,
    SUM(CASE WHEN o.cinsiyet = 'Kız' THEN 1 ELSE 0 END) AS kiz_sayisi
FROM siniflar s
LEFT JOIN ogretmenler ogr ON s.rehber_ogretmen_id = ogr.id
LEFT JOIN ogrenciler o ON (o.sinif || '/' || o.sube) = s.sinif_adi
GROUP BY s.id
ORDER BY s.sinif_seviye, s.sube;
```
