"""Alur kerja aplikasi: menggabungkan io_file, analisis, dan validasi."""

from pathlib import Path

from .analisis import (
    hapus_duplikat,
    indeks_kode,
    rekap_per_kategori,
    stok_menipis,
    total_nilai_stok,
)
from .io_file import muat_barang, tulis_csv, tulis_json
from .validasi import KOLOM_WAJIB, DataTidakValidError, validasi_baris


def proses_file(path_input):
    """Baca -> validasi -> hapus duplikat.

    Return: dict {'barang': list, 'ditolak': list, 'duplikat': list}.
    """
    valid, ditolak = muat_barang(path_input)
    unik, duplikat = hapus_duplikat(valid)
    return {"barang": unik, "ditolak": ditolak, "duplikat": duplikat}


def tambah_barang(barang, baris_mentah):
    """Validasi lalu tambahkan satu barang baru ke list.

    Raise DataTidakValidError jika data salah atau kode sudah dipakai.
    Return: dict barang yang ditambahkan.
    """
    baru = validasi_baris(baris_mentah)
    if baru["kode"] in indeks_kode(barang):
        raise DataTidakValidError(f"kode '{baru['kode']}' sudah ada")
    barang.append(baru)
    return baru


def simpan_laporan(barang, ditolak, dir_output):
    """Simpan 4 file hasil ke folder output. Return: list path file."""
    folder = Path(dir_output)
    menipis = stok_menipis(barang)
    ringkasan = {
        "total_item": len(barang),
        "total_nilai_stok": total_nilai_stok(barang),
        "rekap_per_kategori": rekap_per_kategori(barang),
        "stok_menipis": [b["kode"] for b in menipis],
    }
    return [
        tulis_csv(barang, folder / "barang_bersih.csv", KOLOM_WAJIB),
        tulis_json(ringkasan, folder / "rekap_kategori.json"),
        tulis_csv(menipis, folder / "stok_menipis.csv", KOLOM_WAJIB),
        tulis_csv(
            [{"data_ke": n, "alasan": a} for n, a in ditolak],
            folder / "baris_ditolak.csv",
            ["data_ke", "alasan"],
        ),
    ]
