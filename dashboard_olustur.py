import sqlite3
import json

def generate_web_dashboard(db_path, output_html):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Genel İstatistikler
    cursor.execute("SELECT COUNT(*) FROM ogrenciler")
    toplam_ogrenci = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ogrenciler WHERE cinsiyet = 'Erkek'")
    toplam_erkek = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ogrenciler WHERE cinsiyet = 'Kız'")
    toplam_kiz = cursor.fetchone()[0]

    cursor.execute("SELECT ROUND(AVG(boy_cm), 1), ROUND(AVG(kilo_kg), 1) FROM ogrenciler")
    genel_boy, genel_kilo = cursor.fetchone()

    cursor.execute("SELECT ROUND(AVG(boy_cm), 1), ROUND(AVG(kilo_kg), 1) FROM ogrenciler WHERE cinsiyet = 'Erkek'")
    erkek_boy, erkek_kilo = cursor.fetchone()

    cursor.execute("SELECT ROUND(AVG(boy_cm), 1), ROUND(AVG(kilo_kg), 1) FROM ogrenciler WHERE cinsiyet = 'Kız'")
    kiz_boy, kiz_kilo = cursor.fetchone()

    # 2. Sınıf dağılımı
    cursor.execute("SELECT sinif, COUNT(*) FROM ogrenciler GROUP BY sinif ORDER BY sinif")
    sinif_dagilimi = cursor.fetchall()

    # 3. Yoklama genel durumu
    cursor.execute("SELECT durum, COUNT(*) FROM yoklama GROUP BY durum")
    yoklama_durumlari = dict(cursor.fetchall())
    toplam_yoklama = sum(yoklama_durumlari.values())
    geldi_sayi = yoklama_durumlari.get('Geldi', 0)
    gelmedi_sayi = yoklama_durumlari.get('Gelmedi', 0)
    izinli_sayi = yoklama_durumlari.get('Izinli', 0)

    # 4. Öğrenci Listesi + 90 günlük yoklama özeti
    cursor.execute("""
        SELECT 
            o.id,
            o.okul_no,
            o.ad,
            o.soyad,
            o.cinsiyet,
            o.sinif || '/' || o.sube as sinif_sube,
            o.boy_cm,
            o.kilo_kg,
            SUM(CASE WHEN y.durum = 'Geldi' THEN 1 ELSE 0 END) as geldi,
            SUM(CASE WHEN y.durum = 'Gelmedi' THEN 1 ELSE 0 END) as gelmedi,
            SUM(CASE WHEN y.durum = 'Izinli' THEN 1 ELSE 0 END) as izinli
        FROM ogrenciler o
        LEFT JOIN yoklama y ON o.id = y.ogrenci_id
        GROUP BY o.id
        ORDER BY CAST(o.okul_no AS INTEGER) ASC
    """)
    ogrenciler = cursor.fetchall()
    conn.close()

    # HTML Şablonu
    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ortaokul Bilgi ve Yoklama Yönetim Paneli</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --border: #e2e8f0;
            --primary: #3b82f6;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
        body {{ background: var(--bg); color: var(--text-main); padding: 24px; }}
        .header {{ margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 24px; font-weight: 700; color: #1e293b; }}
        .header p {{ color: var(--text-muted); font-size: 14px; margin-top: 4px; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
        .badge-blue {{ background: #eff6ff; color: #1d4ed8; }}
        .badge-pink {{ background: #fdf2f8; color: #be185d; }}
        .badge-green {{ background: #ecfdf5; color: #047857; }}
        .badge-red {{ background: #fef2f2; color: #b91c1c; }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            background: var(--surface);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .card-label {{ font-size: 13px; font-weight: 500; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
        .card-value {{ font-size: 26px; font-weight: 700; margin-top: 8px; color: var(--text-main); }}
        .card-sub {{ font-size: 13px; color: var(--text-muted); margin-top: 6px; }}

        .search-bar {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 20px;
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        .search-bar input, .search-bar select {{
            padding: 10px 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-bar input:focus, .search-bar select:focus {{ border-color: var(--primary); }}
        .search-bar input {{ flex: 1; }}

        .table-container {{
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }}
        th {{
            background: #f1f5f9;
            color: #475569;
            padding: 14px 16px;
            font-weight: 600;
            border-bottom: 1px solid var(--border);
        }}
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: #334155;
        }}
        tr:hover td {{ background: #f8fafc; }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            display: flex;
            margin-top: 4px;
        }}
        .progress-geldi {{ background: #10b981; }}
        .progress-gelmedi {{ background: #ef4444; }}
        .progress-izinli {{ background: #f59e0b; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🏫 Ortaokul Öğrenci ve Yoklama Sistemi</h1>
            <p>SQLite Veritabanı (okul.db) Üzerinden 200 Öğrenci ve 90 Günlük Yoklama Kayıtları</p>
        </div>
        <span class="badge badge-green">● SQLite Bağlantısı Aktif</span>
    </div>

    <!-- İstatistik Kartları -->
    <div class="stats-grid">
        <div class="card">
            <div class="card-label">Öğrenci Sayısı</div>
            <div class="card-value">{toplam_ogrenci}</div>
            <div class="card-sub"><b style="color:#2563eb;">{toplam_erkek} Erkek</b> (%{toplam_erkek*100/toplam_ogrenci:.1f}) | <b style="color:#db2777;">{toplam_kiz} Kız</b> (%{toplam_kiz*100/toplam_ogrenci:.1f})</div>
        </div>
        <div class="card">
            <div class="card-label">Boy / Kilo Ortalaması</div>
            <div class="card-value">{genel_boy} cm / {genel_kilo} kg</div>
            <div class="card-sub">Erkek: {erkek_boy} cm / {erkek_kilo} kg | Kız: {kiz_boy} cm / {kiz_kilo} kg</div>
        </div>
        <div class="card">
            <div class="card-label">90 Günlük Devamlılık Oranı</div>
            <div class="card-value" style="color: #10b981;">%{geldi_sayi*100/toplam_yoklama:.1f}</div>
            <div class="card-sub">{geldi_sayi} gün katılım, {gelmedi_sayi} devamsızlık</div>
        </div>
        <div class="card">
            <div class="card-label">Kayıt Sayısı</div>
            <div class="card-value">{toplam_yoklama}</div>
            <div class="card-sub">200 Öğrenci x 90 İş Günü</div>
        </div>
    </div>

    <!-- Filtreleme ve Arama -->
    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Öğrenci Adı, Soyadı veya Okul No ile ara..." onkeyup="filterTable()">
        <select id="genderFilter" onchange="filterTable()">
            <option value="">Tüm Cinsiyetler</option>
            <option value="Erkek">Erkek</option>
            <option value="Kız">Kız</option>
        </select>
        <select id="classFilter" onchange="filterTable()">
            <option value="">Tüm Sınıflar</option>
            <option value="5/">5. Sınıflar</option>
            <option value="6/">6. Sınıflar</option>
            <option value="7/">7. Sınıflar</option>
            <option value="8/">8. Sınıflar</option>
        </select>
    </div>

    <!-- Tablo -->
    <div class="table-container">
        <table id="studentsTable">
            <thead>
                <tr>
                    <th>Okul No</th>
                    <th>Adı Soyadı</th>
                    <th>Cinsiyet</th>
                    <th>Sınıf / Şube</th>
                    <th>Boy</th>
                    <th>Kilo</th>
                    <th>90 Günlük Yoklama (Geldi / Gelmedi / İzinli)</th>
                    <th>Devamsızlık Oranı</th>
                </tr>
            </thead>
            <tbody>
"""

    for og in ogrenciler:
        o_id, no, ad, soyad, cins, sinif_sube, boy, kilo, geldi, gelmedi, izinli = og
        badge_class = "badge-blue" if cins == "Erkek" else "badge-pink"
        oran = round((gelmedi / 90.0) * 100, 1)
        p_geldi = (geldi / 90.0) * 100
        p_gelmedi = (gelmedi / 90.0) * 100
        p_izinli = (izinli / 90.0) * 100

        html_content += f"""
                <tr>
                    <td><strong>{no}</strong></td>
                    <td>{ad} {soyad}</td>
                    <td><span class="badge {badge_class}">{cins}</span></td>
                    <td>{sinif_sube}</td>
                    <td>{boy} cm</td>
                    <td>{kilo} kg</td>
                    <td style="min-width: 220px;">
                        <span style="font-size: 12px; color: #475569;">
                            <span style="color:#10b981;">{geldi} G</span> | 
                            <span style="color:#ef4444;">{gelmedi} D</span> | 
                            <span style="color:#f59e0b;">{izinli} İ</span>
                        </span>
                        <div class="progress-bar">
                            <div class="progress-geldi" style="width: {p_geldi}%;"></div>
                            <div class="progress-gelmedi" style="width: {p_gelmedi}%;"></div>
                            <div class="progress-izinli" style="width: {p_izinli}%;"></div>
                        </div>
                    </td>
                    <td><strong>%{oran}</strong></td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>
    </div>

    <script>
        function filterTable() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const gender = document.getElementById('genderFilter').value;
            const classVal = document.getElementById('classFilter').value;
            const rows = document.querySelectorAll('#studentsTable tbody tr');

            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                const rowGender = row.cells[2].innerText.trim();
                const rowClass = row.cells[3].innerText.trim();

                const matchesSearch = text.includes(search);
                const matchesGender = !gender || rowGender === gender;
                const matchesClass = !classVal || rowClass.startsWith(classVal);

                if (matchesSearch && matchesGender && matchesClass) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Panel başarıyla oluşturuldu: {output_html}")

if __name__ == "__main__":
    generate_web_dashboard("C:/Users/bt.stajyer.DIKKAN/Desktop/okul/okul.db", "C:/Users/bt.stajyer.DIKKAN/Desktop/okul/index.html")
