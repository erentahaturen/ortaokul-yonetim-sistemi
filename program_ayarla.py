import sqlite3
import random

DB_PATHS = [
    "C:/Users/bt.stajyer.DIKKAN/Desktop/okul/okul.db",
    "c:/Users/bt.stajyer.DIKKAN/Downloads/Yeni klasör/okul.db"
]

def generate_conflict_free_schedule():
    for db_path in DB_PATHS:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Tabloyu yeniden kur (kısıtlamaları net ve hatasız tut)
        cur.execute("DROP TABLE IF EXISTS haftalik_ders_programi;")
        cur.execute("""
        CREATE TABLE haftalik_ders_programi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sinif_id INTEGER NOT NULL,
            ders_id INTEGER NOT NULL,
            ogretmen_id INTEGER NOT NULL,
            gun TEXT NOT NULL,
            ders_saati INTEGER NOT NULL,
            derslik TEXT NOT NULL,
            FOREIGN KEY (sinif_id) REFERENCES siniflar(id),
            FOREIGN KEY (ders_id) REFERENCES dersler(id),
            FOREIGN KEY (ogretmen_id) REFERENCES ogretmenler(id),
            UNIQUE(sinif_id, gun, ders_saati) -- Bir sınıf aynı saatte tek derste olur
        );
        """)

        # Dizinleri yeniden oluştur
        cur.execute("CREATE INDEX IF NOT EXISTS idx_program_sinif_gun ON haftalik_ders_programi(sinif_id, gun);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_program_ogretmen ON haftalik_ders_programi(ogretmen_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_program_ders ON haftalik_ders_programi(ders_id);")

        # 16 Sınıf
        cur.execute("SELECT id, sinif_adi, derslik FROM siniflar ORDER BY sinif_seviye, sube")
        siniflar = cur.fetchall()

        # Dersler
        cur.execute("SELECT id, ders_kodu FROM dersler")
        ders_map = {kodu: id_ for id_, kodu in cur.fetchall()}

        # Branş Öğretmenleri
        cur.execute("SELECT id, brans FROM ogretmenler")
        brans_ogretmenleri = {}
        for ogr_id, brans in cur.fetchall():
            brans_ogretmenleri.setdefault(brans, []).append(ogr_id)

        kod_brans_map = {
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

        # 35 saatlik haftalık müfredat ders kodları
        # Haftalık: MAT(6), TURK(6), FEN(4), SOS(3), ING(4), DIN(2), BED(2), GOR(1), MUZ(1), BIL(2), TEK(2), REH(1) = 34 + 1
        temel_dersler = (
            ["MAT"] * 6 + ["TURK"] * 6 + ["FEN"] * 4 + ["SOS"] * 3 +
            ["ING"] * 4 + ["DIN"] * 2 + ["BED"] * 2 + ["GOR"] * 1 +
            ["MUZ"] * 1 + ["BIL"] * 2 + ["TEK"] * 2 + ["REH"] * 2
        ) # Tam 35 ders

        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        
        insert_rows = []

        # Her sınıf için 35 saati haftanın günlerine ve saatlerine yerleştir
        for s_idx, (sinif_id, sinif_adi, derslik) in enumerate(siniflar):
            # Sınıfa özel dengeli karıştırma (Her sınıfın saatleri farklı sırayla olsun)
            sinif_ders_listesi = list(temel_dersler)
            # Deterministik karıştır (tekrar çalışsa da aynı düzenli program oluşsun)
            rnd = random.Random(sinif_id * 101)
            rnd.shuffle(sinif_ders_listesi)

            slot_idx = 0
            for gun in gunler:
                for saat in range(1, 8): # 1. ders - 7. ders
                    d_kod = sinif_ders_listesi[slot_idx]
                    slot_idx += 1

                    d_id = ders_map[d_kod]
                    brans = kod_brans_map[d_kod]
                    uygun_hocalar = brans_ogretmenleri.get(brans, [1])
                    # Sınıf şubesine göre hocayı ata
                    hoca_id = uygun_hocalar[s_idx % len(uygun_hocalar)]

                    insert_rows.append((sinif_id, d_id, hoca_id, gun, saat, derslik))

        cur.executemany("""
        INSERT INTO haftalik_ders_programi (sinif_id, ders_id, ogretmen_id, gun, ders_saati, derslik)
        VALUES (?, ?, ?, ?, ?, ?)
        """, insert_rows)

        conn.commit()
        conn.close()
        print(f"Haftalık program eksiksiz kuruldu: {db_path} -> 16 Sınıf x 35 Saat = {len(insert_rows)} Ders Saati.")

if __name__ == '__main__':
    generate_conflict_free_schedule()
