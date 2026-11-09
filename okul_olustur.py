import sqlite3
import random
from datetime import datetime, timedelta

def create_school_database(db_name="okul.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 1. Tabloları oluştur
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ogrenciler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        okul_no TEXT UNIQUE NOT NULL,
        ad TEXT NOT NULL,
        soyad TEXT NOT NULL,
        cinsiyet TEXT NOT NULL,
        sinif TEXT NOT NULL,
        sube TEXT NOT NULL,
        boy_cm REAL NOT NULL,
        kilo_kg REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS yoklama (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ogrenci_id INTEGER NOT NULL,
        tarih TEXT NOT NULL,
        durum TEXT NOT NULL, -- 'Geldi', 'Gelmedi', 'Izinli'
        FOREIGN KEY (ogrenci_id) REFERENCES ogrenciler(id)
    )
    """)

    # Mevcut veriyi kontrol et, temizle veya baştan oluştur
    cursor.execute("DELETE FROM yoklama")
    cursor.execute("DELETE FROM ogrenciler")

    # İsim ve Soyisim Havuzu
    erkek_isimleri = [
        "Ahmet", "Mehmet", "Mustafa", "Ali", "Can", "Burak", "Emre", "Kerem", "Yusuf", "Ömer",
        "Eren", "Kaan", "Arda", "Ege", "Mert", "Oğuz", "Deniz", "Umut", "Barış", "Yiğit",
        "Batuhan", "Emir", "Onur", "Berk", "Doruk", "Alper", "Tuna", "Sarp", "Bora", "Yağız"
    ]
    kiz_isimleri = [
        "Zeynep", "Elif", "Defne", "Asya", "Azra", "Nehir", "Eylül", "Duru", "Yağmur", "Ceren",
        "Selin", "Melis", "İrem", "Buse", "Nil", "Ece", "Derin", "Ada", "Güneş", "Miray",
        "Berra", "Esra", "Damla", "Hazal", "Öykü", "Ceylin", "Beste", "Simge", "Pelin", "Berna"
    ]
    soyisimler = [
        "Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir",
        "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek",
        "Polat", "Korkmaz", "Erdoğan", "Acar", "Bulut", "Güler", "Yalçın", "Güneş", "Bozkurt", "Ünal"
    ]

    siniflar = ["5", "6", "7", "8"]
    subeler = ["A", "B", "C", "D"]

    # 101 Erkek ve 99 Kız Öğrenci Listesi
    ogrenciler_data = []

    # Okul no için başlangıç
    okul_no = 100

    # 101 Erkek
    for _ in range(101):
        okul_no += 1
        ad = random.choice(erkek_isimleri)
        soyad = random.choice(soyisimler)
        sinif = random.choice(siniflar)
        sube = random.choice(subeler)
        # Ortaokul yaş grubuna uygun boy-kilo aralığı
        sinif_num = int(sinif)
        # 5. sınıf ~11 yaş, 8. sınıf ~14 yaş
        boy = round(random.uniform(138 + (sinif_num - 5) * 7, 155 + (sinif_num - 5) * 8), 1)
        kilo = round(random.uniform(32 + (sinif_num - 5) * 4, 52 + (sinif_num - 5) * 6), 1)
        ogrenciler_data.append((str(okul_no), ad, soyad, "Erkek", sinif, sube, boy, kilo))

    # 99 Kız
    for _ in range(99):
        okul_no += 1
        ad = random.choice(kiz_isimleri)
        soyad = random.choice(soyisimler)
        sinif = random.choice(siniflar)
        sube = random.choice(subeler)
        sinif_num = int(sinif)
        boy = round(random.uniform(136 + (sinif_num - 5) * 6, 153 + (sinif_num - 5) * 7), 1)
        kilo = round(random.uniform(30 + (sinif_num - 5) * 4, 48 + (sinif_num - 5) * 5), 1)
        ogrenciler_data.append((str(okul_no), ad, soyad, "Kız", sinif, sube, boy, kilo))

    # Karıştır
    random.shuffle(ogrenciler_data)

    cursor.executemany("""
    INSERT INTO ogrenciler (okul_no, ad, soyad, cinsiyet, sinif, sube, boy_cm, kilo_kg)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ogrenciler_data)

    # Eklenen öğrencilerin ID'lerini al
    cursor.execute("SELECT id FROM ogrenciler")
    ogrenci_idleri = [row[0] for row in cursor.fetchall()]

    # 90 Günlük Yoklama (Hafta sonlarını hariç tutarak son 90 okul günü)
    # Geriye doğru 90 iş günü üretelim
    okul_gunleri = []
    current_date = datetime.now().date()
    while len(okul_gunleri) < 90:
        # 0 = Pazartesi, 4 = Cuma, 5 = Cumartesi, 6 = Pazar
        if current_date.weekday() < 5:
            okul_gunleri.append(current_date.strftime("%Y-%m-%d"))
        current_date -= timedelta(days=1)
    okul_gunleri.reverse() # Kronolojik sıra

    yoklama_data = []
    durumlar = ["Geldi", "Gelmedi", "Izinli"]
    agirliklar = [0.92, 0.05, 0.03] # %92 geldi, %5 gelmedi, %3 izinli gerçekçi dağılım

    for o_id in ogrenci_idleri:
        for gun in okul_gunleri:
            durum = random.choices(durumlar, weights=agirliklar)[0]
            yoklama_data.append((o_id, gun, durum))

    cursor.executemany("""
    INSERT INTO yoklama (ogrenci_id, tarih, durum)
    VALUES (?, ?, ?)
    """, yoklama_data)

    conn.commit()
    conn.close()
    print(f"Başarıyla tamamlandı! {len(ogrenciler_data)} öğrenci ve {len(yoklama_data)} yoklama kaydı '{db_name}' dosyasına eklendi.")

if __name__ == "__main__":
    create_school_database()
