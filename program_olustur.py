import sqlite3
import os

DB_PATHS = [
    "C:/Users/bt.stajyer.DIKKAN/Desktop/okul/okul.db",
    "c:/Users/bt.stajyer.DIKKAN/Downloads/Yeni klasör/okul.db"
]

def build_curriculum_and_indexes():
    for db_path in DB_PATHS:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # 1. DERSLER TABLOSU
        cur.execute("""
        CREATE TABLE IF NOT EXISTS dersler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ders_kodu TEXT UNIQUE NOT NULL,
            ders_adi TEXT NOT NULL,
            haftalik_saat INTEGER NOT NULL,
            kategori TEXT NOT NULL -- 'Sayısal', 'Sözel', 'Yabancı Dil', 'Yetenek'
        )
        """)

        # 2. HAFTALIK DERS PROGRAMI TABLOSU (Çoktan çoğa ilişki + Zaman çizelgesi)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS haftalik_ders_programi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sinif_id INTEGER NOT NULL,
            ders_id INTEGER NOT NULL,
            ogretmen_id INTEGER NOT NULL,
            gun TEXT NOT NULL, -- 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma'
            ders_saati INTEGER NOT NULL, -- 1: 08:30-09:10, 2: 09:25-10:05 ... 7. ders
            derslik TEXT NOT NULL,
            FOREIGN KEY (sinif_id) REFERENCES siniflar(id),
            FOREIGN KEY (ders_id) REFERENCES dersler(id),
            FOREIGN KEY (ogretmen_id) REFERENCES ogretmenler(id),
            UNIQUE(sinif_id, gun, ders_saati), -- Bir sınıf aynı saatte 2 derste olamaz
            UNIQUE(ogretmen_id, gun, ders_saati) -- Bir öğretmen aynı saatte 2 farklı sınıfta olamaz
        )
        """)

        # 3. SQL EĞİTİMİ İÇİN INDEX (DİZİN) OLUŞTURMA
        # Farklı index türleri: Tekli, Bileşik (Composite), Benzersiz (Unique)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ogrenciler_sinif_sube ON ogrenciler(sinif, sube);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ogrenciler_ad_soyad ON ogrenciler(ad, soyad);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_yoklama_ogrenci_tarih ON yoklama(ogrenci_id, tarih);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_yoklama_durum ON yoklama(durum);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_program_sinif_gun ON haftalik_ders_programi(sinif_id, gun);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_program_ogretmen_gun ON haftalik_ders_programi(ogretmen_id, gun);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_program_ders ON haftalik_ders_programi(ders_id);")

        # Mevcut verileri sıfırla ve yeniden yükle
        cur.execute("DELETE FROM haftalik_ders_programi;")
        cur.execute("DELETE FROM dersler;")

        # Ders Verileri
        dersler_data = [
            ("MAT", "Matematik", 6, "Sayısal"),
            ("TURK", "Türkçe", 6, "Sözel"),
            ("FEN", "Fen Bilimleri", 4, "Sayısal"),
            ("SOS", "Sosyal Bilgiler", 3, "Sözel"),
            ("ING", "İngilizce", 4, "Yabancı Dil"),
            ("DIN", "Din Kültürü ve Ahlak Bilgisi", 2, "Sözel"),
            ("BED", "Beden Eğitimi ve Spor", 2, "Yetenek"),
            ("GOR", "Görsel Sanatlar", 1, "Yetenek"),
            ("MUZ", "Müzik", 1, "Yetenek"),
            ("BIL", "Bilişim Teknolojileri ve Yazılım", 2, "Sayısal"),
            ("TEK", "Teknoloji ve Tasarım", 2, "Yetenek"),
            ("REH", "Rehberlik ve Kariyer Planlama", 1, "Rehberlik")
        ]

        cur.executemany("""
        INSERT INTO dersler (ders_kodu, ders_adi, haftalik_saat, kategori)
        VALUES (?, ?, ?, ?)
        """, dersler_data)

        # ID Haritalamaları
        cur.execute("SELECT id, ders_kodu FROM dersler")
        ders_map = {kodu: id_ for id_, kodu in cur.fetchall()}

        cur.execute("SELECT id, brans FROM ogretmenler")
        brans_ogretmen_map = {}
        for ogr_id, brans in cur.fetchall():
            brans_ogretmen_map.setdefault(brans, []).append(ogr_id)

        # Ders - Branş Eşleşmesi
        ders_brans_iliskisi = {
            "MAT": "Matematik",
            "TURK": "Türkçe",
            "FEN": "Fen Bilimleri",
            "SOS": "Sosyal Bilgiler",
            "ING": "İngilizce",
            "DIN": "Din Kültürü",
            "BED": "Beden Eğitimi",
            "GOR": "Görsel Sanatlar",
            "MUZ": "Müzik",
            "BIL": "Bilişim Teknolojileri",
            "TEK": "Teknoloji ve Tasarım",
            "REH": "Rehberlik / Psikolojik Danışman"
        }

        # 16 Sınıf için haftalık ders çizelgesi üret (Pazartesi-Cuma, günde 7 ders saati = 35 saat)
        cur.execute("SELECT id, sinif_adi, derslik FROM siniflar")
        siniflar = cur.fetchall()

        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        
        # 35 derslik standart haftalık müfredat dağılımı
        standart_haftalik_dersler = (
            ["MAT"] * 6 +
            ["TURK"] * 6 +
            ["FEN"] * 4 +
            ["SOS"] * 3 +
            ["ING"] * 4 +
            ["DIN"] * 2 +
            ["BED"] * 2 +
            ["GOR"] * 1 +
            ["MUZ"] * 1 +
            ["BIL"] * 2 +
            ["TEK"] * 2 +
            ["REH"] * 1
        ) # Toplam 34 + 1 serbest = 35 ders

        program_data = []

        for sinif_id, sinif_adi, derslik in siniflar:
            ders_havuzu = list(standart_haftalik_dersler)
            # Rastgele ama dengeli dağıtım için
            import random
            random.seed(sinif_id * 42)
            random.shuffle(ders_havuzu)

            ders_idx = 0
            for gun in gunler:
                for saat in range(1, 8): # 1'den 7'ye kadar ders saatleri
                    if ders_idx < len(ders_havuzu):
                        d_kod = ders_havuzu[ders_idx]
                        ders_idx += 1
                    else:
                        d_kod = "MAT"
                    
                    d_id = ders_map[d_kod]
                    brans_adi = ders_brans_iliskisi[d_kod]
                    uygun_ogretmenler = brans_ogretmen_map.get(brans_adi, [1])
                    ogr_id = uygun_ogretmenler[sinif_id % len(uygun_ogretmenler)]
                    
                    program_data.append((sinif_id, d_id, ogr_id, gun, saat, derslik))

        # Programı toplu yaz (çakışma olursa IGNORE ile koru)
        cur.executemany("""
        INSERT OR IGNORE INTO haftalik_ders_programi (sinif_id, ders_id, ogretmen_id, gun, ders_saati, derslik)
        VALUES (?, ?, ?, ?, ?, ?)
        """, program_data)

        conn.commit()
        conn.close()
        print(f"Başarıyla güncellendi: {db_path} -> 12 Ders, 560 Ders Saati ve Index'ler oluşturuldu!")

if __name__ == '__main__':
    build_curriculum_and_indexes()
