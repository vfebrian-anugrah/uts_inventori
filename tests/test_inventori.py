"""Pengujian otomatis (unittest, standard library)."""

import json
import tempfile
import unittest
from pathlib import Path

from inventori import (
    DataTidakValidError,
    cari_nama,
    hapus_duplikat,
    kategori_unik,
    proses_file,
    rekap_per_kategori,
    simpan_laporan,
    stok_menipis,
    tambah_barang,
    total_nilai_stok,
    validasi_baris,
)
from inventori.io_file import baca_mentah

BARIS_OK = {"kode": "x-1", "nama": "Pensil", "kategori": "ATK",
            "stok": "10", "harga": "2000", "stok_minimum": "5"}


class UjiValidasi(unittest.TestCase):
    def test_baris_normal_dinormalisasi(self):
        hasil = validasi_baris(BARIS_OK)
        self.assertEqual(hasil["kode"], "X-1")
        self.assertEqual(hasil["stok"], 10)

    def test_stok_bukan_angka_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            validasi_baris({**BARIS_OK, "stok": "abc"})

    def test_harga_negatif_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            validasi_baris({**BARIS_OK, "harga": "-1"})

    def test_kode_kosong_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            validasi_baris({**BARIS_OK, "kode": "  "})

    def test_stok_nol_adalah_edge_case_valid(self):
        self.assertEqual(validasi_baris({**BARIS_OK, "stok": "0"})["stok"], 0)


class UjiAnalisis(unittest.TestCase):
    def setUp(self):
        self.data = proses_file("data/barang.csv")["barang"]

    def test_jumlah_data_bersih(self):
        self.assertEqual(len(self.data), 11)

    def test_duplikat_dibuang(self):
        valid = [validasi_baris(BARIS_OK), validasi_baris(BARIS_OK)]
        unik, duplikat = hapus_duplikat(valid)
        self.assertEqual((len(unik), len(duplikat)), (1, 1))

    def test_stok_menipis_memakai_angka_bukan_teks(self):
        kode = [b["kode"] for b in stok_menipis(self.data)]
        self.assertEqual(sorted(kode), ["ATK-002", "ELK-003", "KRT-002", "KRT-003"])

    def test_total_nilai_dan_rekap(self):
        rekap = rekap_per_kategori(self.data)
        self.assertEqual(sum(r["nilai_stok"] for r in rekap.values()),
                         total_nilai_stok(self.data))
        self.assertEqual(total_nilai_stok(self.data), 4_916_000)

    def test_kategori_unik(self):
        self.assertEqual(kategori_unik(self.data),
                         ["Alat Tulis", "Elektronik", "Kertas", "Perlengkapan"])

    def test_cari_nama_tidak_peka_huruf(self):
        self.assertEqual(len(cari_nama(self.data, "LAKBAN")), 1)

    def test_cari_kata_kunci_kosong(self):
        with self.assertRaises(ValueError):
            cari_nama(self.data, "   ")

    def test_data_kosong_tidak_error(self):
        self.assertEqual(total_nilai_stok([]), 0)
        self.assertEqual(rekap_per_kategori([]), {})
        self.assertEqual(stok_menipis([]), [])

    def test_tambah_kode_ganda_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            tambah_barang(self.data, {**BARIS_OK, "kode": "atk-001"})


class UjiFile(unittest.TestCase):
    def test_file_tidak_ada(self):
        with self.assertRaises(FileNotFoundError):
            proses_file("data/tidak_ada.csv")

    def test_json_rusak(self):
        with self.assertRaises(DataTidakValidError):
            proses_file("data/barang_rusak.json")

    def test_csv_hanya_header(self):
        hasil = proses_file("data/barang_kosong.csv")
        self.assertEqual(hasil["barang"], [])

    def test_format_tidak_didukung(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.txt"
            path.write_text("x", encoding="utf-8")
            with self.assertRaises(DataTidakValidError):
                baca_mentah(path)

    def test_header_tidak_lengkap(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.csv"
            path.write_text("kode,nama\nA,B\n", encoding="utf-8")
            with self.assertRaises(DataTidakValidError):
                proses_file(path)

    def test_simpan_laporan_menghasilkan_file(self):
        hasil = proses_file("data/barang.csv")
        with tempfile.TemporaryDirectory() as tmp:
            paths = simpan_laporan(hasil["barang"], hasil["ditolak"], tmp)
            self.assertTrue(all(p.exists() for p in paths))
            ringkasan = json.loads((Path(tmp) / "rekap_kategori.json").read_text("utf-8"))
            self.assertEqual(ringkasan["total_item"], 11)


if __name__ == "__main__":
    unittest.main()
