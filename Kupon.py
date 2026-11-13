import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() 

TOTAL = 10000
BOXES = 10
PER_BOX = TOTAL // BOXES
ZONK = 6

WINNERS = {
    1: (100_000, 50),
    2: (50_000, 100),
    3: (20_000, 250),
    4: (10_000, 500),
    5: (5_000, 1000),
}

PRIZES = {
    **WINNERS,
    ZONK: (0, TOTAL - sum(q for _, q in WINNERS.values())),
}

assert all(q % BOXES == 0 for _, q in PRIZES.values()), "qty harus habis dibagi jumlah box"

BATCHES = [
    (1, "Amir", "Surabaya", datetime(2026, 1, 1, 14, 0), range(1, 6)),
    (2, "Nando", "Surabaya", datetime(2026, 1, 2, 10, 0), range(6, 11)),
]

CONN_STR = os.getenv("DB_CONN")


def generate(seed=None):
    rng = random.Random(seed)

    per_box = [pid for pid, (_, q) in PRIZES.items() for _ in range(q // BOXES)]
    assert len(per_box) == PER_BOX

    nums = list(range(1, TOTAL + 1))
    rng.shuffle(nums)

    prize_of, box_of, members = {}, {}, {}
    for b in range(1, BOXES + 1):
        m = nums[(b - 1) * PER_BOX : b * PER_BOX]
        plist = per_box[:]
        rng.shuffle(plist)
        members[b] = m
        for n, p in zip(m, plist):
            prize_of[n], box_of[n] = p, b

    for _ in range(1000):
        bad = [
            n for n in range(1, TOTAL)
            if prize_of[n] != ZONK and prize_of[n] == prize_of[n + 1]
        ]
        if not bad:
            break
        for n in bad:
            m = rng.choice(members[box_of[n]])
            prize_of[n], prize_of[m] = prize_of[m], prize_of[n]
    else:
        raise RuntimeError("gagal menghindari hadiah berurutan, coba seed lain")

    return [(f"{n:05d}", prize_of[n], box_of[n]) for n in range(1, TOTAL + 1)]


def save_to_db(rows):
    import pyodbc

    conn = pyodbc.connect(CONN_STR, autocommit=False)
    cur = conn.cursor()
    cur.fast_executemany = True
    try:
        prize_rows = []
        for pid, (nom, q) in PRIZES.items():
            ket = "Anda Belum Beruntung" if nom == 0 else f"Hadiah Rp {nom:,}".replace(",", ".")
            prize_rows.append((pid, nom, ket, q, q // BOXES))
        cur.executemany(
            "INSERT INTO m_prize (prize_id, nominal, keterangan, qty_total, qty_per_box) "
            "VALUES (?,?,?,?,?)",
            prize_rows,
        )

        box_ids = {}
        for no, op, lok, ts, boxes in BATCHES:
            cur.execute("SELECT operator_id FROM m_operator WHERE nama = ?", op)
            r = cur.fetchone()
            if not r:
                raise ValueError(f"operator '{op}' tidak ada di m_operator")

            cur.execute(
                "INSERT INTO prod_batch (no_batch, operator_id, lokasi, produced_at, output_box) "
                "OUTPUT INSERTED.batch_id VALUES (?,?,?,?,?)",
                no, r[0], lok, ts, len(boxes),
            )
            batch_id = cur.fetchone()[0]

            for b in boxes:
                cur.execute(
                    "INSERT INTO box (batch_id, no_box, jumlah_kupon) "
                    "OUTPUT INSERTED.box_id VALUES (?,?,?)",
                    batch_id, b, PER_BOX,
                )
                box_ids[b] = cur.fetchone()[0]

        cur.executemany(
            "INSERT INTO coupon (no_kupon, prize_id, box_id) VALUES (?,?,?)",
            [(n, p, box_ids[b]) for n, p, b in rows],
        )

        conn.commit()
        print(f"OK: {len(rows)} kupon tersimpan")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    rows = generate()
    save_to_db(rows)