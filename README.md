# 📦 LK-DATABASE-BACKUP

**LK-DATABASE-BACKUP** adalah script backup database otomatis yang dikembangkan khusus untuk server FiveM. Script ini dirancang agar proses backup berjalan aman, ringan, stabil, dan telah dioptimalkan untuk penggunaan jangka panjang di server roleplay maupun development server.

---

# ✨ Features

- ✅ Auto backup database
- ✅ Auto scheduled backup
- ✅ Lightweight & optimized
- ✅ Easy configuration
- ✅ Stable for production server
- ✅ Prevent duplicate backup process
- ✅ Auto save backup files
- ✅ Support Discord webhook

### 🔥 Advanced Features

- ✅ Auto delete backup lama  
  Script akan otomatis menghapus **7 backup database lama** dan hanya menyisakan **3 backup terbaru** agar storage RDP/VPS/server tetap ringan dan tidak cepat penuh.

- ✅ Auto split database file  
  Jika ukuran database terlalu besar, file backup akan otomatis di-split menjadi beberapa bagian agar tetap bisa dikirim melalui webhook Discord tanpa gagal upload.

- ✅ Optimized for long-term usage  
  Dibuat untuk meminimalisir beban server saat proses backup berjalan.

---

# 📁 Installation

1. Download resource ini
2. Setup file `auto-backup.py`
3. jalankan perintah `python auto-backup.py` di cmd/python

# FOLDER BARU AUTO DIBUAT OLEH SYSTEM DENGAN NAMA 'DATABASE_BACKUP' DISITU TEMPAT FILE BACKUP DATABASE BERADA
