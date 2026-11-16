"""Format teks untuk tampilan. Fungsi di sini hanya mengembalikan string."""


def format_rupiah(angka):
    """12500 -> 'Rp 12.500'."""
    return "Rp " + f"{angka:,}".replace(",", ".")


def format_tabel(records):
    """Tabel barang berformat teks rata kolom."""
    if not records:
        return "(tidak ada data)"
    baris = [f"{'KODE':<8} {'NAMA':<22} {'KATEGORI':<13} {'STOK':>5} {'HARGA':>11} {'MIN':>4}"]
    for b in records:
        baris.append(
            f"{b['kode']:<8} {b['nama']:<22} {b['kategori']:<13} "
            f"{b['stok']:>5} {format_rupiah(b['harga']):>11} {b['stok_minimum']:>4}"
        )
    return "\n".join(baris)


def format_rekap(rekap, total):
    """Rekap per kategori + total nilai persediaan."""
    if not rekap:
        return "(tidak ada data)"
    baris = [f"{'KATEGORI':<13} {'ITEM':>4} {'TOTAL STOK':>10} {'NILAI STOK':>14}"]
    for kategori, isi in rekap.items():
        baris.append(
            f"{kategori:<13} {isi['jumlah_item']:>4} {isi['total_stok']:>10} "
            f"{format_rupiah(isi['nilai_stok']):>14}"
        )
    baris.append(f"Total nilai persediaan: {format_rupiah(total)}")
    return "\n".join(baris)


def format_menipis(records):
    """Daftar barang stok menipis dengan keterangan HABIS / MENIPIS."""
    if not records:
        return "Semua stok aman."
    return "\n".join(
        f"- {b['kode']} {b['nama']}: stok {b['stok']} (min {b['stok_minimum']}) "
        f"[{'HABIS' if b['stok'] == 0 else 'MENIPIS'}]"
        for b in records
    )
