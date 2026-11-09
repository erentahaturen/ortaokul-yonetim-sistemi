import sqlite3
import random

DB_PATH = "C:/Users/bt.stajyer.DIKKAN/Desktop/okul/okul.db"

def update_db_with_classes_and_teachers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Öğretmenler Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ogretmenler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT NOT NULL,
        soyad TEXT NOT NULL,
        brans TEXT NOT NULL,
        cinsiyet TEXT NOT NULL,
        telefon TEXT,
        eposta TEXT
    )
    """)

    # 2. Sınıflar Tablosu (sinif_adi: 5/A, 5/B ..., rehber_ogretmen_id)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS siniflar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sinif_seviye INTEGER NOT NULL, -- 5, 6, 7, 8
        sube TEXT NOT NULL, -- A, B, C, D
        sinif_adi TEXT UNIQUE NOT NULL, -- "5/A"
        derslik TEXT NOT NULL,
        rehber_ogretmen_id INTEGER,
        FOREIGN KEY (rehber_ogretmen_id) REFERENCES ogretmenler(id)
    )
    """)

    cursor.execute("DELETE FROM siniflar")
    cursor.execute("DELETE FROM ogretmenler")

    # Öğretmen Verileri (Ortaokul branşları)
    ogretmen_listesi = [
        ("Kemal", "Yıldız", "Matematik", "Erkek", "0532 111 2233", "kemal.yildiz@okul.meb.k12.tr"),
        ("Ayşe", "Demir", "Türkçe", "Kız", "0533 222 3344", "ayse.demir@okul.meb.k12.tr"),
        ("Murat", "Kaya", "Fen Bilimleri", "Erkek", "0535 333 4455", "murat.kaya@okul.meb.k12.tr"),
        ("Fatma", "Öztürk", "Sosyal Bilgiler", "Kız", "0542 444 5566", "fatma.ozturk@okul.meb.k12.tr"),
        ("Selim", "Çelik", "İngilizce", "Erkek", "0555 555 6677", "selim.celik@okul.meb.k12.tr"),
        ("Zeynep", "Aydın", "Din Kültürü", "Kız", "0536 666 7788", "zeynep.aydin@okul.meb.k12.tr"),
        ("Hakan", "Şahin", "Beden Eğitimi", "Erkek", "0537 777 8899", "hakan.sahin@okul.meb.k12.tr"),
        ("Ebru", "Arslan", "Görsel Sanatlar", "Kız", "0538 888 9900", "ebru.arslan@okul.meb.k12.tr"),
        ("Cem", "Koç", "Müzik", "Erkek", "0539 999 0011", "cem.koc@okul.meb.k12.tr"),
        ("Derya", "Polat", "Bilişim Teknolojileri", "Kız", "0544 123 4567", "derya.polat@okul.meb.k12.tr"),
        ("Burak", "Korkmaz", "Matematik", "Erkek", "0545 234 5678", "burak.korkmaz@okul.meb.k12.tr"),
        ("Merve", "Doğan", "Türkçe", "Kız", "0546 345 6789", "merve.dogan@okul.meb.k12.tr"),
        ("Serkan", "Aslan", "Fen Bilimleri", "Erkek", "0547 456 7890", "serkan.aslan@okul.meb.k12.tr"),
        ("Gülşen", "Erdoğan", "İngilizce", "Kız", "0548 567 8901", "gulsen.erdogan@okul.meb.k12.tr"),
        ("Tolga", "Güler", "Rehberlik / Psikolojik Danışman", "Erkek", "0549 678 9012", "tolga.guler@okul.meb.k12.tr"),
        ("Seda", "Kurt", "Teknoloji ve Tasarım", "Kız", "0551 789 0123", "seda.kurt@okul.meb.k12.tr")
    ]

    cursor.executemany("""
    INSERT INTO ogretmenler (ad, soyad, brans, cinsiyet, telefon, eposta)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ogretmen_listesi)

    cursor.execute("SELECT id FROM ogretmenler")
    ogretmen_ids = [r[0] for r in cursor.fetchall()]

    # Sınıflar (5/A..D, 6/A..D, 7/A..D, 8/A..D = 16 Sınıf)
    seviyeler = [5, 6, 7, 8]
    subeler = ["A", "B", "C", "D"]
    sinif_data = []

    teacher_idx = 0
    for sev in seviyeler:
        for sub in subeler:
            sinif_adi = f"{sev}/{sub}"
            derslik = f"Kat {sev-4} - No: {sev}0{subeler.index(sub)+1}"
            rehber_id = ogretmen_ids[teacher_idx % len(ogretmen_ids)]
            teacher_idx += 1
            sinif_data.append((sev, sub, sinif_adi, derslik, rehber_id))

    cursor.executemany("""
    INSERT INTO siniflar (sinif_seviye, sube, sinif_adi, derslik, rehber_ogretmen_id)
    VALUES (?, ?, ?, ?, ?)
    """, sinif_data)

    conn.commit()
    conn.close()
    print("Öğretmenler (16 branş öğretmeni) ve Sınıflar (16 şube) başarıyla eklendi!")

if __name__ == '__main__':
    update_db_with_classes_and_teachers()
