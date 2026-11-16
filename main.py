"""Titik masuk aplikasi Inventori Toko Alat Tulis (command line).

Cara pakai:
    python main.py                      -> menu interaktif
    python main.py --demo               -> jalankan otomatis (tanpa input)
    python main.py --input data/barang.json
"""

import argparse
import sys

from inventori import (
    DataTidakValidError,
    cari_nama,
    format_menipis,
    format_rekap,
    format_tabel,
    proses_file,
    rekap_per_kategori,
    simpan_laporan,
    stok_menipis,
    tambah_barang,
    total_nilai_stok,
)

INPUT_BAWAAN = "data/barang.csv"
OUTPUT_BAWAAN = "output"
FORM_BARANG = (
    ("kode", "Kode (kosongkan untuk batal)"),
    ("nama", "Nama"),
    ("kategori", "Kategori"),
    ("stok", "Stok"),
    ("harga", "Harga (Rp)"),
    ("stok_minimum", "Stok minimum"),
)


def muat_dengan_aman(path):
    """Muat file dan tangani error umum. Return: hasil dict atau None."""
    try:
        return proses_file(path)
    except FileNotFoundError as error:
        print(f"Gagal: {error}")
    except DataTidakValidError as error:
        print(f"Gagal: {error}")
    except OSError as error:
        print(f"Gagal membuka file: {error}")
    return None


def cetak_ringkasan_muat(hasil):
    print(f"Data valid   : {len(hasil['barang'])} barang")
    print(f"Duplikat     : {len(hasil['duplikat'])} baris dibuang")
    print(f"Baris ditolak: {len(hasil['ditolak'])}")
    for nomor, alasan in hasil["ditolak"]:
        print(f"  - data ke-{nomor}: {alasan}")


def cetak_analisis(barang):
    print("\n== DAFTAR BARANG ==")
    print(format_tabel(barang))
    print("\n== REKAP PER KATEGORI ==")
    print(format_rekap(rekap_per_kategori(barang), total_nilai_stok(barang)))
    print("\n== STOK MENIPIS ==")
    print(format_menipis(stok_menipis(barang)))


def simpan_dengan_aman(barang, ditolak, dir_output):
    try:
        for path in simpan_laporan(barang, ditolak, dir_output):
            print(f"Tersimpan: {path}")
    except OSError as error:
        print(f"Gagal menyimpan laporan: {error}")


def jalankan_demo(path_input, dir_output):
    print(f"Membaca {path_input} ...")
    hasil = muat_dengan_aman(path_input)
    if hasil is None:
        return 1
    cetak_ringkasan_muat(hasil)
    if not hasil["barang"]:
        print("Tidak ada data valid untuk diproses.")
        return 0
    cetak_analisis(hasil["barang"])
    print("\n== MENYIMPAN LAPORAN ==")
    simpan_dengan_aman(hasil["barang"], hasil["ditolak"], dir_output)
    return 0


def minta_barang_baru(barang):
    """Form tambah barang; ulangi sampai valid atau dibatalkan."""
    while True:
        isian = {}
        for kunci, label in FORM_BARANG:
            isian[kunci] = input(f"{label}: ")
            if kunci == "kode" and not isian["kode"].strip():
                print("Dibatalkan.")
                return
        try:
            baru = tambah_barang(barang, isian)
        except DataTidakValidError as error:
            print(f"Input salah: {error}. Ulangi pengisian.")
        else:
            print(f"Barang {baru['kode']} ditambahkan.")
            return


def tampilkan_menu():
    print(
        "\n=== INVENTORI TOKO ALAT TULIS ===\n"
        "1. Muat data dari file (CSV/JSON)\n"
        "2. Tampilkan semua barang\n"
        "3. Cari barang berdasarkan nama\n"
        "4. Rekap per kategori\n"
        "5. Barang stok menipis\n"
        "6. Tambah barang\n"
        "7. Simpan laporan (CSV & JSON)\n"
        "0. Keluar"
    )


def menu_interaktif(path_awal, dir_output):
    barang, ditolak = [], []
    if path_awal:
        hasil = muat_dengan_aman(path_awal)
        if hasil:
            barang, ditolak = hasil["barang"], hasil["ditolak"]
            cetak_ringkasan_muat(hasil)
    while True:
        tampilkan_menu()
        try:
            pilihan = input("Pilihan: ").strip()
        except EOFError:
            break
        if pilihan == "1":
            path = input(f"Path file [{INPUT_BAWAAN}]: ").strip() or INPUT_BAWAAN
            hasil = muat_dengan_aman(path)
            if hasil:
                barang, ditolak = hasil["barang"], hasil["ditolak"]
                cetak_ringkasan_muat(hasil)
        elif pilihan == "2":
            print(format_tabel(barang))
        elif pilihan == "3":
            try:
                print(format_tabel(cari_nama(barang, input("Kata kunci: "))))
            except ValueError as error:
                print(f"Input salah: {error}.")
        elif pilihan == "4":
            print(format_rekap(rekap_per_kategori(barang), total_nilai_stok(barang)))
        elif pilihan == "5":
            print(format_menipis(stok_menipis(barang)))
        elif pilihan == "6":
            minta_barang_baru(barang)
        elif pilihan == "7":
            simpan_dengan_aman(barang, ditolak, dir_output)
        elif pilihan == "0":
            print("Selesai.")
            break
        else:
            print("Pilihan tidak tersedia.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inventori toko alat tulis")
    parser.add_argument("--input", default=INPUT_BAWAAN, help="file CSV/JSON masukan")
    parser.add_argument("--output", default=OUTPUT_BAWAAN, help="folder keluaran")
    parser.add_argument("--demo", action="store_true", help="jalankan tanpa menu")
    args = parser.parse_args(argv)
    if args.demo:
        return jalankan_demo(args.input, args.output)
    try:
        menu_interaktif(args.input, args.output)
    except (EOFError, KeyboardInterrupt):
        print("\nInput dihentikan. Program selesai.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
