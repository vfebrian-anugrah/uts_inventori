# Inventori Toko Alat Tulis (UTS Pemrograman Dasar - TK091)

Aplikasi command line berbasis Python untuk mengolah data inventaris toko alat tulis:
membaca data barang dari CSV/JSON, membersihkan data (validasi dan duplikat), membuat
rekap per kategori, mendeteksi stok menipis, lalu menyimpan laporan ke CSV dan JSON.

- Tujuan   : membantu pemilik toko mengetahui barang yang hampir habis dan nilai persediaan.
- Pengguna : pemilik atau staf gudang toko kecil.
- Teknologi: Python 3.10+ dan **standard library saja** (tanpa dependency eksternal).

## Struktur Program

```
uts_inventori/
|-- main.py                  Titik masuk + menu interaktif (hanya urusan tampilan/UI)
|-- requirements.txt         Dependency (kosong: hanya standard library)
|-- README.md
|-- inventori/               Package buatan sendiri
|   |-- __init__.py          Mengekspor fungsi publik package
|   |-- validasi.py          Validasi & normalisasi satu baris data + DataTidakValidError
|   |-- io_file.py           Baca/tulis CSV dan JSON
|   |-- analisis.py          Operasi data: duplikat, grup, rekap, filter, cari
|   |-- laporan.py           Format teks (rupiah, tabel, rekap)
|   `-- aplikasi.py          Alur kerja: proses_file, tambah_barang, simpan_laporan
|-- data/                    Contoh file input
|   |-- barang.csv           Data utama (15 baris: normal, duplikat, dan tidak valid)
|   |-- barang.json          Contoh input JSON
|   |-- barang_kosong.csv    Edge case: hanya header
|   `-- barang_rusak.json    Edge case: JSON tidak valid
|-- tests/test_inventori.py  20 pengujian otomatis (unittest)
|-- debug/skenario_bug.py    Skenario debugging (bug perbandingan str vs int)
`-- output/                  Contoh hasil keluaran dan bukti eksekusi
```

## Alur Dependensi Antar-Module

```
main.py
  |-- inventori.aplikasi ----> inventori.io_file ----> inventori.validasi
  |         |
  |         `---------------> inventori.analisis      (tanpa dependensi lain)
  `-- inventori.laporan                                (tanpa dependensi lain)
```

Aturan: panah hanya mengarah ke bawah (tidak ada dependensi melingkar). `analisis` dan
`laporan` tidak membaca file maupun memanggil `print()`, sehingga mudah diuji.

## Cara Menjalankan

Syarat: Python 3.10 atau lebih baru. Tidak perlu `pip install`.
Jalankan semua perintah dari folder `uts_inventori`.

```
python main.py                       # menu interaktif (memuat data/barang.csv)
python main.py --demo                # jalankan otomatis tanpa menu, simpan ke output/
python main.py --input data/barang.json --output output/dari_json --demo
python -m unittest discover -s tests -v    # jalankan pengujian
python debug/skenario_bug.py         # skenario debugging
python debug/skenario_bug.py --debug # berhenti di breakpoint() (perintah pdb: p, n, c, q)
```

Di macOS/Linux gunakan `python3`. Bila ada spasi pada nama folder, jalankan dari dalam folder tersebut.

## Format Input

CSV (UTF-8) dengan header wajib: `kode,nama,kategori,stok,harga,stok_minimum`

| Kolom | Aturan |
|---|---|
| kode | tidak boleh kosong, dijadikan huruf besar, harus unik |
| nama, kategori | tidak boleh kosong |
| stok | bilangan bulat >= 0 |
| harga | bilangan bulat > 0 (rupiah) |
| stok_minimum | bilangan bulat >= 0 |

JSON: list of object dengan kunci yang sama. Contoh: `data/barang.json`.

## Format Output

Di terminal: tabel barang, rekap per kategori, dan daftar stok menipis. File di folder `output/`:

| File | Isi |
|---|---|
| barang_bersih.csv | barang valid dan unik |
| rekap_kategori.json | total item, total nilai stok, rekap per kategori, kode stok menipis |
| stok_menipis.csv | barang dengan stok di bawah stok minimum |
| baris_ditolak.csv | nomor data dan alasan penolakan |

## Fitur Utama

1. Muat file CSV/JSON, validasi tiap baris, dan buang duplikat berdasarkan kode.
2. Rekap per kategori (jumlah item, total stok, nilai stok) dan total nilai persediaan.
3. Deteksi barang stok menipis atau habis.
4. Pencarian barang berdasarkan nama (tidak peka huruf besar/kecil).
5. Tambah barang lewat form dengan validasi dan pengulangan input.
6. Simpan laporan ke CSV dan JSON.

## Struktur Data yang Dipakai

- **list**: daftar barang (urutan terjaga, mudah diiterasi dan diurutkan).
- **dictionary**: satu barang (kunci -> nilai), rekap per kategori, dan indeks `kode -> barang`.
- **set**: kode yang sudah terlihat (deteksi duplikat cepat) dan kategori unik.

## Penanganan Error (Defensive Programming)

| Situasi | Penanganan |
|---|---|
| File tidak ditemukan | `FileNotFoundError` ditangkap, pesan jelas, program tidak crash |
| JSON rusak / format tidak didukung / header CSV kurang | `DataTidakValidError` dengan pesan spesifik |
| Baris data tidak valid | Baris dilewati, dicatat di `baris_ditolak.csv`, baris lain tetap diproses |
| Input angka salah di form | Form diulang dengan pesan alasan |
| Kode barang ganda saat tambah | Ditolak dengan pesan |
| File tidak bisa ditulis | `OSError` ditangkap saat menyimpan |
| Ctrl+C / input terputus | Ditangani, program berhenti rapi tanpa traceback |
| Data kosong | Laporan tetap tampil ("tidak ada data"), tidak terjadi pembagian nol |

Skenario debugging: lihat `debug/skenario_bug.py` dan `output/hasil_debug.txt`
(bug membandingkan teks `"120" < "20"` sehingga hasil stok menipis salah).

## Edge Case yang Diuji

Stok 0 (berstatus HABIS), CSV hanya header, file tidak ada, JSON rusak, ekstensi tidak
didukung, harga negatif, stok bukan angka, kode kosong, kode ganda, kata kunci pencarian kosong.

## Sumber Referensi dan Bantuan AI

- Dokumentasi Python: modul `csv`, `json`, `pathlib`, `argparse`, `unittest`, `pdb`.
- Modul Praktikum Pemrograman Dasar (Praktikum 5, 6, 7).
- Bantuan AI: Claude (Anthropic) digunakan untuk membantu menyusun rancangan, source code,
  README, dan draf lembar jawaban. Kode telah dijalankan dan diuji (20 pengujian lulus).
