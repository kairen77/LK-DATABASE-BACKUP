import os
import time
import requests
import schedule
import subprocess
import random
import string
from datetime import datetime

# =========================
# CONFIG
# =========================
MYSQL_PATH = r"C:\xampp\mysql\bin\mysqldump.exe"
MYSQL_ADMIN = r"C:\xampp\mysql\bin\mysqladmin.exe"

DB_USER = "root"
DB_PASS = ""
DB_NAME = "DATABASE NAME" # GANTI NAMA DATABASE KALIAN DISINI, JANGAN LUPA SESUAIKAN JUGA DB_USER DAN DB_PASS JIKA PERLU

BACKUP_FOLDER = r"C:\backup\database_backup" # PASTIKAN FOLDER INI ADA, JANGAN LUPA GANTI SESUAI KONFIGURASI KALIAN
ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe" # PASTIKAN JUGA PATH 7-ZIP SESUAI DENGAN KONFIGURASI KALIAN, JIKA TIDAK ADA BISA DOWNLOAD DI https://www.7-zip.org/download.html
ZIP_PASSWORD = "lk-development" # GANTI PASSWORD ZIP SESUAI KEINGINAN KALIAN, JANGAN LUPA CATAT AGAR TIDAK LUPA PASSWORDNYA, PASSWORD INI AKAN DIPAKAI UNTUK SEMUA BACKUP, JADI JIKA SUDAH ADA BACKUP SEBELUMNYA PASTIKAN MENGGUNAKAN PASSWORD YANG SAMA AGAR BISA DIEXTRACT

DISCORD_WEBHOOK = "WEBHOOK DISCORD" # ISI WEBHOOK DISCORD KALIAN DISINI, JANGAN LUPA BUAT WEBHOOK DI CHANNEL DISCORD KALIAN DAN PASTIKAN PERMISSION WEBHOOK SUDAH BENAR (KIRIM PESAN, EMBED LINK, DAN UPLOAD FILE)  
SERVER_NAME = "NAMA SERVER" # ISI NAMA SERVER KALIAN DISINI

# =========================
# INIT
# =========================
os.makedirs(BACKUP_FOLDER, exist_ok=True)
fail_count = 0

# =========================
# FORMAT SIZE
# =========================
def format_size(size):
    for unit in ['B','KB','MB','GB']:
        if size < 1024:
            return f"{round(size,2)} {unit}"
        size /= 1024

# =========================
# GENERATE CODE
# =========================
def generate_unique_code(length=3):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# =========================
# SEND EMBED
# =========================
def send_embed(title, fields=None, color=5793266):
    payload = {
        "embeds": [
            {
                "title": title,
                "color": color,
                "fields": fields if fields else [],
                "footer": {"text": f"{SERVER_NAME} • Auto Backup"}
            }
        ]
    }

    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
    except:
        print("Webhook error")

# =========================
# CLEANUP (KEEP 3 TERBARU)
# =========================
def keep_last_backups(folder):
    files = sorted(
        [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".zip")],
        key=os.path.getmtime,
        reverse=True
    )

    if len(files) <= 3:
        return

    keep_files = files[:3]
    delete_files = files[3:]

    deleted_names = []

    for f in delete_files:
        try:
            os.remove(f)
            deleted_names.append(os.path.basename(f))
        except:
            pass

    remaining_names = [os.path.basename(f) for f in keep_files]

    send_embed(
        "🧹 Cleanup Backup",
        [
            {
                "name": f"🗑️ Dihapus ({len(deleted_names)})",
                "value": "\n".join(deleted_names[:10]) if deleted_names else "Tidak ada",
                "inline": False
            },
            {
                "name": f"📦 Tersisa ({len(remaining_names)})",
                "value": "\n".join(remaining_names),
                "inline": False
            }
        ],
        15105570
    )

# =========================
# CHECK DB
# =========================
def check_database():
    try:
        result = subprocess.run(
            [MYSQL_ADMIN, "-u", DB_USER, "ping"],
            capture_output=True,
            text=True
        )
        return "alive" in result.stdout.lower()
    except:
        return False

# =========================
# BACKUP
# =========================
def backup_database():
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = f"{DB_NAME}_{datetime.now().strftime('%d_%m_%Y')}_{generate_unique_code()}"

    sql_file = os.path.join(BACKUP_FOLDER, file_name + ".sql")
    zip_file = os.path.join(BACKUP_FOLDER, file_name + ".zip")

    send_embed("🟡 Backup Dimulai", [
        {"name": "Waktu", "value": waktu}
    ])

    try:
        # =========================
        # DUMP
        # =========================
        cmd = [MYSQL_PATH, "-u", DB_USER, DB_NAME]

        if DB_PASS:
            cmd.insert(3, f"-p{DB_PASS}")

        with open(sql_file, "w", encoding="utf-8") as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )

        if result.returncode != 0:
            send_embed("🔴 Backup Gagal", [
                {"name": "Error", "value": result.stderr}
            ], 16711680)
            return

        if os.path.getsize(sql_file) < 100:
            send_embed("🔴 Backup Gagal", [
                {"name": "Error", "value": "SQL kosong / gagal dump"}
            ], 16711680)
            return

        # =========================
        # ZIP
        # =========================
        size_sql = os.path.getsize(sql_file)

        zip_cmd = [
            ZIP_PATH,
            "a",
            "-tzip",
            "-mx=5",
            f"-p{ZIP_PASSWORD}",
            "-mem=AES256"
        ]

        if size_sql > 8 * 1024 * 1024:
            zip_cmd.append("-v8m")

        zip_cmd += [zip_file, sql_file]
        subprocess.run(zip_cmd)

        files = [
            f for f in os.listdir(BACKUP_FOLDER)
            if f.startswith(file_name) and ".zip" in f
        ]

        total_size = sum(
            os.path.getsize(os.path.join(BACKUP_FOLDER, f))
            for f in files
        )

        size_text = format_size(total_size)
        is_split = any(".zip." in f for f in files)

        # =========================
        # SUCCESS
        # =========================
        send_embed(
            "🟢 Backup Berhasil",
            [
                {"name": "File", "value": file_name + ".zip"},
                {"name": "Ukuran", "value": size_text, "inline": True},
                {"name": "Split", "value": "Ya" if is_split else "Tidak", "inline": True},
                {"name": "Database", "value": DB_NAME}
            ],
            5763719
        )

        # =========================
        # UPLOAD
        # =========================
        for i, f in enumerate(files, 1):
            path = os.path.join(BACKUP_FOLDER, f)

            requests.post(DISCORD_WEBHOOK, json={
                "content": f"📤 Upload {i}/{len(files)} → `{f}`"
            })

            with open(path, "rb") as file_data:
                requests.post(DISCORD_WEBHOOK, files={"file": file_data})

            time.sleep(1)

        os.remove(sql_file)

        # =========================
        # CLEANUP
        # =========================
        keep_last_backups(BACKUP_FOLDER)

    except Exception as e:
        send_embed("🔴 System Error", [
            {"name": "Error", "value": str(e)}
        ], 16711680)

# =========================
# RUN
# =========================
backup_database()
schedule.every(1).hours.do(backup_database)

print("AUTO BACKUP AKTIF")

while True:
    schedule.run_pending()

    if not check_database():
        fail_count += 1
    else:
        fail_count = 0

    if fail_count >= 3:
        send_embed(
            "🔴 Database Down",
            [{"name": "Status", "value": "MySQL tidak merespon"}],
            16711680
        )
        fail_count = 0

    time.sleep(10)