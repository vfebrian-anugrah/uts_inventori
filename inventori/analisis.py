"""Operasi data murni: set, dictionary, list, comprehension. Tanpa I/O."""


def nilai_stok(barang):
    """Nilai persediaan satu barang = stok x harga (int)."""
    return barang["stok"] * barang["harga"]


def hapus_duplikat(records):
    """Pisahkan data unik dan duplikat berdasarkan kode barang.

    Memakai set 'sudah_ada' agar pengecekan cepat (O(1)).
    Return: (unik, duplikat). Kemunculan pertama dipertahankan.
    """
    sudah_ada = set()
    unik, duplikat = [], []
    for barang in records:
        if barang["kode"] in sudah_ada:
            duplikat.append(barang)
        else:
            sudah_ada.add(barang["kode"])
            unik.append(barang)
    return unik, duplikat


def kategori_unik(records):
    """Set comprehension: kumpulan kategori tanpa pengulangan (diurutkan)."""
    return sorted({barang["kategori"] for barang in records})


def indeks_kode(records):
    """Dictionary comprehension: kode -> barang, untuk pencarian cepat."""
    return {barang["kode"]: barang for barang in records}


def kelompokkan_per_kategori(records):
    """Kelompokkan barang: dict kategori -> list barang."""
    kelompok = {}
    for barang in records:
        kelompok.setdefault(barang["kategori"], []).append(barang)
    return kelompok


def rekap_per_kategori(records):
    """Rekapitulasi per kategori (jumlah item, total stok, nilai stok)."""
    kelompok = kelompokkan_per_kategori(records)
    return {
        kategori: {
            "jumlah_item": len(items),
            "total_stok": sum(b["stok"] for b in items),
            "nilai_stok": sum(nilai_stok(b) for b in items),
        }
        for kategori, items in sorted(kelompok.items())
    }


def total_nilai_stok(records):
    """Total nilai persediaan seluruh barang (0 jika data kosong)."""
    return sum(nilai_stok(b) for b in records)


def stok_menipis(records):
    """List comprehension: barang dengan stok di bawah stok minimum."""
    return [b for b in records if b["stok"] < b["stok_minimum"]]


def cari_nama(records, kata_kunci):
    """Cari barang yang namanya memuat kata kunci (tidak peka huruf besar)."""
    kata = kata_kunci.strip().lower()
    if not kata:
        raise ValueError("kata kunci tidak boleh kosong")
    return [b for b in records if kata in b["nama"].lower()]
