# 🏫 Ortaokul Yönetim Sistemi & SQL Eğitim Veritabanı

Bu proje; 200 öğrenci, 16 sınıf/şube, 16 öğretmen, 90 günlük detaylı yoklama kayıtları ve MEB uyumlu haftalık ders programını içeren kapsamlı bir **SQLite** ve **Web Yönetim Paneli** uygulamasıdır. Ayrıca veri analizi ve SQL eğitimleri için özel olarak kurgulanmıştır.

---

## 🌟 Özellikler

1. **Öğrenci Yönetimi:**
   - 200 Öğrenci (101 Erkek, 99 Kız)
   - Ortaokul yaş gruplarına uygun gerçekçi **boy (cm)** ve **kilo (kg)** metrikleri
   - Canlı öğrenci ekleme ve silme desteği (SQLite ile senkronize)

2. **90 Günlük Net Yoklama Takibi:**
   - Her öğrenci için 90 iş gününü kapsayan **toplam 18.000 satırlık** yoklama kaydı (`Geldi`, `Gelmedi`, `Izinli`)
   - Öğrenci bazında **"📅 90 Günü İncele"** takvim dökümü

3. **Sınıflar & Öğretmen Kadrosu:**
   - 16 Şube (5/A..D, 6/A..D, 7/A..D, 8/A..D)
   - Her sınıfın derslik konumu ve Sınıf Rehber Öğretmeni
   - 16 Branş Öğretmeni (Matematik, Türkçe, Fen, Sosyal, İngilizce vb.)

4. **Haftalık Ders Çizelgesi (Müfredat):**
   - 16 sınıf için haftalık 35 saat, toplam **560 ders saati**
   - Sınıf seçerek Pazartesi-Cuma ders saatlerini renk kodlarıyla inceleme

5. **SQL Eğitimi & Performans İndeksleri:**
   - `INDEX` yapıları (`idx_ogrenciler_sinif_sube`, `idx_yoklama_ogrenci_tarih`, vb.)
   - `EXPLAIN QUERY PLAN` sorgu optimizasyon örnekleri
   - Temelden ileri seviyeye `WHERE`, `GROUP BY`, `HAVING`, çoklu `JOIN`, `CASE WHEN` pratikleri ([SQL_EGITIM_REHBERI.md](SQL_EGITIM_REHBERI.md))

---

## 🚀 Projeyi Çalıştırma

Python yüklü herhangi bir bilgisayarda harici hiçbir kütüphane kurmadan tek komutla çalıştırılabilir:

```bash
python server.py
```

Ardından tarayıcınızda açın:
👉 **http://localhost:5000**

---

## 🗄️ Veritabanı Tablo Yapısı (`okul.db`)

| Tablo | Kayıt Sayısı | Açıklama |
|---|---|---|
| `ogrenciler` | 200 | Öğrenci kimlik, sınıf, boy ve kilo bilgileri |
| `yoklama` | 18.000 | 90 günlük gün gün yoklama durumu |
| `siniflar` | 16 | Şubeler, derslikler ve rehber öğretmen ID |
| `ogretmenler` | 16 | Branş öğretmenleri ve iletişim bilgileri |
| `dersler` | 12 | MEB ortaokul ders müfredatı ve kategorileri |
| `haftalik_ders_programi` | 560 | Gün ve saat bazlı haftalık ders dağılımı |
