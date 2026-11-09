import http.server
import socketserver
import json
import sqlite3
import urllib.parse
from datetime import datetime, timedelta
import random
import os

PORT = 5000
DB_PATH = "C:/Users/bt.stajyer.DIKKAN/Desktop/okul/okul.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class SchoolRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # API: Haftalık Ders Programı (Sınıfa göre veya tümü)
        if parsed.path == '/api/ders-programi':
            sinif_id = params.get('sinif_id', [None])[0]
            conn = get_db()
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.id,
                    s.sinif_adi,
                    d.ders_adi,
                    d.ders_kodu,
                    d.kategori,
                    ogr.ad || ' ' || ogr.soyad as ogretmen_adi,
                    ogr.brans,
                    p.gun,
                    p.ders_saati,
                    p.derslik
                FROM haftalik_ders_programi p
                JOIN siniflar s ON p.sinif_id = s.id
                JOIN dersler d ON p.ders_id = d.id
                JOIN ogretmenler ogr ON p.ogretmen_id = ogr.id
            """
            if sinif_id:
                query += " WHERE p.sinif_id = ? ORDER BY p.gun, p.ders_saati"
                cursor.execute(query, (sinif_id,))
            else:
                query += " ORDER BY s.sinif_seviye, s.sube, p.gun, p.ders_saati"
                cursor.execute(query)

            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(rows, ensure_ascii=False).encode('utf-8'))
            return

        # API: Bir öğrencinin detaylı 90 günlük yoklama listesi
        if parsed.path.startswith('/api/ogrenci-yoklama/'):
            ogrenci_id = parsed.path.split('/')[-1]
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tarih, durum 
                FROM yoklama 
                WHERE ogrenci_id = ? 
                ORDER BY tarih DESC
            """, (ogrenci_id,))
            gunler = [dict(r) for r in cursor.fetchall()]
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(gunler, ensure_ascii=False).encode('utf-8'))
            return

        # API: Öğretmenler Listesi
        if parsed.path == '/api/ogretmenler':
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ogr.id, ogr.ad, ogr.soyad, ogr.brans, ogr.cinsiyet, ogr.telefon, ogr.eposta,
                       s.sinif_adi as rehberlik_sinifi
                FROM ogretmenler ogr
                LEFT JOIN siniflar s ON ogr.id = s.rehber_ogretmen_id
                ORDER BY ogr.ad ASC
            """)
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(rows, ensure_ascii=False).encode('utf-8'))
            return

        # API: Sınıflar Listesi
        if parsed.path == '/api/siniflar':
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id,
                    s.sinif_adi,
                    s.derslik,
                    ogr.ad || ' ' || ogr.soyad as rehber_ogretmen,
                    ogr.brans as rehber_brans,
                    COUNT(o.id) as ogrenci_sayisi,
                    SUM(CASE WHEN o.cinsiyet = 'Erkek' THEN 1 ELSE 0 END) as erkek_sayisi,
                    SUM(CASE WHEN o.cinsiyet = 'Kız' THEN 1 ELSE 0 END) as kiz_sayisi
                FROM siniflar s
                LEFT JOIN ogretmenler ogr ON s.rehber_ogretmen_id = ogr.id
                LEFT JOIN ogrenciler o ON (o.sinif || '/' || o.sube) = s.sinif_adi
                GROUP BY s.id
                ORDER BY s.sinif_seviye ASC, s.sube ASC
            """)
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(rows, ensure_ascii=False).encode('utf-8'))
            return

        # API: Genel Öğrenci ve Yoklama Listesi
        if parsed.path == '/api/ogrenciler':
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    o.id,
                    o.okul_no,
                    o.ad,
                    o.soyad,
                    o.cinsiyet,
                    o.sinif,
                    o.sube,
                    o.boy_cm,
                    o.kilo_kg,
                    COALESCE(SUM(CASE WHEN y.durum = 'Geldi' THEN 1 ELSE 0 END), 0) as geldi,
                    COALESCE(SUM(CASE WHEN y.durum = 'Gelmedi' THEN 1 ELSE 0 END), 0) as gelmedi,
                    COALESCE(SUM(CASE WHEN y.durum = 'Izinli' THEN 1 ELSE 0 END), 0) as izinli
                FROM ogrenciler o
                LEFT JOIN yoklama y ON o.id = y.ogrenci_id
                GROUP BY o.id
                ORDER BY o.id DESC
            """)
            rows = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT COUNT(*) FROM ogrenciler")
            toplam = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM ogrenciler WHERE cinsiyet = 'Erkek'")
            erkek_sayisi = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM ogrenciler WHERE cinsiyet = 'Kız'")
            kiz_sayisi = cursor.fetchone()[0]

            cursor.execute("SELECT ROUND(AVG(boy_cm), 1), ROUND(AVG(kilo_kg), 1) FROM ogrenciler")
            avg_row = cursor.fetchone()
            avg_boy = avg_row[0] if avg_row and avg_row[0] else 0
            avg_kilo = avg_row[1] if avg_row and avg_row[1] else 0

            cursor.execute("SELECT COUNT(*) FROM ogretmenler")
            toplam_ogretmen = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM siniflar")
            toplam_sinif = cursor.fetchone()[0]

            conn.close()

            response_data = {
                "ogrenciler": rows,
                "stats": {
                    "toplam": toplam,
                    "erkek": erkek_sayisi,
                    "kiz": kiz_sayisi,
                    "avg_boy": avg_boy,
                    "avg_kilo": avg_kilo,
                    "toplam_ogretmen": toplam_ogretmen,
                    "toplam_sinif": toplam_sinif
                }
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            return

        if parsed.path == '/' or parsed.path == '/index.html':
            self.path = '/index.html'
        
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # Öğrenci Ekle
        if parsed.path == '/api/ogrenci-ekle':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            okul_no = data.get('okul_no')
            ad = data.get('ad')
            soyad = data.get('soyad')
            cinsiyet = data.get('cinsiyet')
            sinif = data.get('sinif')
            sube = data.get('sube')
            boy = float(data.get('boy_cm', 150))
            kilo = float(data.get('kilo_kg', 45))

            conn = get_db()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO ogrenciler (okul_no, ad, soyad, cinsiyet, sinif, sube, boy_cm, kilo_kg)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (okul_no, ad, soyad, cinsiyet, sinif, sube, boy, kilo))
                yeni_id = cursor.lastrowid

                # 90 günlük yoklama
                okul_gunleri = []
                cur = datetime.now().date()
                while len(okul_gunleri) < 90:
                    if cur.weekday() < 5:
                        okul_gunleri.append(cur.strftime("%Y-%m-%d"))
                    cur -= timedelta(days=1)
                
                yoklama_batch = []
                for gun in okul_gunleri:
                    durum = random.choices(["Geldi", "Gelmedi", "Izinli"], weights=[0.92, 0.05, 0.03])[0]
                    yoklama_batch.append((yeni_id, gun, durum))

                cursor.executemany("INSERT INTO yoklama (ogrenci_id, tarih, durum) VALUES (?, ?, ?)", yoklama_batch)

                conn.commit()
                response = {"status": "success", "message": "Öğrenci eklendi", "id": yeni_id}
            except sqlite3.IntegrityError:
                response = {"status": "error", "message": f"{okul_no} numaralı öğrenci zaten kayıtlı!"}
            finally:
                conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        # Öğretmen Ekle
        if parsed.path == '/api/ogretmen-ekle':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ogretmenler (ad, soyad, brans, cinsiyet, telefon, eposta)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data.get('ad'), data.get('soyad'), data.get('brans'), data.get('cinsiyet'), data.get('telefon'), data.get('eposta')))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Öğretmen eklendi"}).encode('utf-8'))
            return

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith('/api/ogrenci-sil/'):
            ogrenci_id = parsed.path.split('/')[-1]
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM yoklama WHERE ogrenci_id = ?", (ogrenci_id,))
            cursor.execute("DELETE FROM ogrenciler WHERE id = ?", (ogrenci_id,))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Öğrenci silindi"}).encode('utf-8'))
            return

        if parsed.path.startswith('/api/ogretmen-sil/'):
            ogretmen_id = parsed.path.split('/')[-1]
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE siniflar SET rehber_ogretmen_id = NULL WHERE rehber_ogretmen_id = ?", (ogretmen_id,))
            cursor.execute("DELETE FROM ogretmenler WHERE id = ?", (ogretmen_id,))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Öğretmen silindi"}).encode('utf-8'))
            return

if __name__ == '__main__':
    os.chdir("C:/Users/bt.stajyer.DIKKAN/Desktop/okul")
    with socketserver.TCPServer(("", PORT), SchoolRequestHandler) as httpd:
        print(f"Sunucu çalışıyor: http://localhost:{PORT}")
        httpd.serve_forever()
