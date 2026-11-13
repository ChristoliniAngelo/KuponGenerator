import os
import sys
import pyodbc
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))
CONN_STR = os.getenv("DB_CONN")
OUT_FILE = Path(__file__).with_name("report.txt")

SQL = """
    SELECT b.no_batch, o.nama, b.lokasi, b.produced_at,
           x.no_box, c.no_kupon, p.nominal, p.keterangan
    FROM prod_batch b
    JOIN m_operator o ON o.operator_id = b.operator_id
    JOIN box x    ON x.batch_id = b.batch_id
    JOIN coupon c ON c.box_id = x.box_id
    JOIN m_prize p ON p.prize_id = c.prize_id
    WHERE b.no_batch = ?
    ORDER BY x.no_box, c.no_kupon
"""


class Tee:
    """Tulis ke terminal dan file sekaligus."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def cetak_batch(cur, no_batch, out):
    cur.execute(SQL, no_batch)
    rows = cur.fetchall()

    if not rows:
        print(f"Batch {no_batch} tidak ditemukan\n", file=out)
        return

    h = rows[0]
    print("=" * 60, file=out)
    print(f"No Batch      : {h.no_batch}", file=out)
    print(f"Nama Operator : {h.nama}", file=out)
    print(f"Lokasi        : {h.lokasi}", file=out)
    print(f"Tanggal / Jam : {h.produced_at:%d-%b-%Y / %H:%M}", file=out)
    print("-" * 60, file=out)
    print(f"{'No Box':<8}{'No Kupon':<10}{'Nominal':>10}  Keterangan", file=out)
    for r in rows:
        nominal = f"{int(r.nominal):,}".replace(",", ".")
        print(f"{r.no_box:<8}{r.no_kupon:<10}{nominal:>10}  {r.keterangan}", file=out)
    print(file=out)


def laporan(*batches):
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        out = Tee(sys.stdout, f)
        with pyodbc.connect(CONN_STR) as conn:
            cur = conn.cursor()
            for b in batches:
                cetak_batch(cur, b, out)
    print(f"Laporan tersimpan di: {OUT_FILE}")


if __name__ == "__main__":
    batches = [int(a) for a in sys.argv[1:]] or [1, 2]
    laporan(*batches)