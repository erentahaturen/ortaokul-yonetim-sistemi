import sqlite3

def rapor():
    conn = sqlite3.connect("okul.db")
    cursor = conn.cursor()

    print("=== OKUL BİLGİ ÖZETİ ===")
    
    # Cinsiyet Dağılımı
    cursor.execute("SELECT cinsiyet, COUNT(*), ROUND(AVG(boy_cm), 1), ROUND(AVG(kilo_kg), 1) FROM ogrenciler GROUP BY cinsiyet")
    print("\n[Cinsiyet, Öğrenci Sayısı, Ort. Boy (cm), Ort. Kilo (kg)]")
    for row in cursor.fetchall():
        print(f"- {row[0]}: {row[1]} kişi | Ort. Boy: {row[2]} cm | Ort. Kilo: {row[3]} kg")

    # Sınıf Dağılımı
    cursor.execute("SELECT sinif, COUNT(*) FROM ogrenciler GROUP BY sinif ORDER BY sinif")
    print("\n[Sınıf Dağılımı]")
    for row in cursor.fetchall():
        print(f"- {row[0]}. Sınıflar: {row[1]} öğrenci")

    # Yoklama İstatistikleri
    cursor.execute("""
        SELECT durum, COUNT(*), ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM yoklama), 2)
        FROM yoklama
        GROUP BY durum
    """)
    print("\n[90 Günlük Toplam Yoklama Dağılımı (200 öğrenci x 90 gün = 18.000 kayıt)]")
    for row in cursor.fetchall():
        print(f"- {row[0]}: {row[1]} kayıt (%{row[2]})")

    # Örnek 3 Öğrencinin Devamsızlık Durumu
    cursor.execute("""
        SELECT o.okul_no, o.ad, o.soyad, o.sinif || '/' || o.sube,
               SUM(CASE WHEN y.durum = 'Gelmedi' THEN 1 ELSE 0 END) as devamsizlik_gunu
        FROM ogrenciler o
        JOIN yoklama y ON o.id = y.ogrenci_id
        GROUP BY o.id
        LIMIT 5
    """)
    print("\n[Örnek 5 Öğrenci ve 90 Günlük Devamsızlık Sayıları]")
    for row in cursor.fetchall():
        print(f"- No: {row[0]} | {row[1]} {row[2]} ({row[3]}) -> {row[4]} gün gelmedi")

    conn.close()

if __name__ == "__main__":
    rapor()
