
# Kupon Generator

## Cara Pakai

### 1. Setup Database

Jalankan script `table_schema.sql` di SQL Server untuk membuat tabel yang dibutuhkan.

### 2. Atur Koneksi Database

Isi `DB_CONN` di file `.env`:

```env
DB_CONN=DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server;DATABASE=your_db;UID=your_user;PWD=your_password
```

### 3. Jalankan kupon.py

```bash
python kupon.py
```

### 4. Jalankan report.py

```bash
python report.py
```
