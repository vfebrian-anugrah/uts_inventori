"""Validasi dan normalisasi satu baris data barang."""

KOLOM_WAJIB = ("kode", "nama", "kategori", "stok", "harga", "stok_minimum")


class DataTidakValidError(ValueError):
    """Data barang atau format file tidak sesuai aturan."""


def _ke_int(nilai, nama_kolom):
    """Ubah nilai menjadi int.

    Parameter: nilai (str/int/None), nama_kolom (str, untuk pesan error).
    Return: int. Raise DataTidakValidError jika bukan bilangan bulat.
    """
    teks = "" if nilai is None else str(nilai).strip()
    try:
        return int(teks)
    except ValueError:
        raise DataTidakValidError(
            f"kolom '{nama_kolom}' harus bilangan bulat (diterima: {teks!r})"
        ) from None


def _teks_wajib(baris, kolom):
    nilai = baris.get(kolom)
    teks = "" if nilai is None else str(nilai).strip()
    if not teks:
        raise DataTidakValidError(f"kolom '{kolom}' tidak boleh kosong")
    return teks


def validasi_baris(baris):
    """Validasi satu dictionary mentah.

    Parameter: baris (dict) dengan kunci sesuai KOLOM_WAJIB.
    Return: dict baru dengan tipe benar (stok, harga, stok_minimum = int).
    Raise: DataTidakValidError bila ada aturan yang dilanggar.
    """
    hilang = [k for k in KOLOM_WAJIB if k not in baris]
    if hilang:
        raise DataTidakValidError(f"kolom tidak ada: {', '.join(hilang)}")

    kode = _teks_wajib(baris, "kode").upper()
    nama = _teks_wajib(baris, "nama")
    kategori = _teks_wajib(baris, "kategori")
    stok = _ke_int(baris["stok"], "stok")
    harga = _ke_int(baris["harga"], "harga")
    minimum = _ke_int(baris["stok_minimum"], "stok_minimum")

    if stok < 0:
        raise DataTidakValidError("stok tidak boleh negatif")
    if harga <= 0:
        raise DataTidakValidError("harga harus lebih dari 0")
    if minimum < 0:
        raise DataTidakValidError("stok_minimum tidak boleh negatif")
    return {
        "kode": kode,
        "nama": nama,
        "kategori": kategori,
        "stok": stok,
        "harga": harga,
        "stok_minimum": minimum,
    }
