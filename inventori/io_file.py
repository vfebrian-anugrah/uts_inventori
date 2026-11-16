"""Pembacaan dan penulisan file CSV / JSON. Tidak berisi logika analisis."""

import csv
import json
from pathlib import Path

from .validasi import KOLOM_WAJIB, DataTidakValidError, validasi_baris


def _baca_csv(path):
    with open(path, "r", newline="", encoding="utf-8") as file:
        pembaca = csv.DictReader(file)
        if pembaca.fieldnames is None:  # file benar-benar kosong
            return []
        hilang = [k for k in KOLOM_WAJIB if k not in pembaca.fieldnames]
        if hilang:
            raise DataTidakValidError(
                f"header CSV tidak lengkap, kolom hilang: {', '.join(hilang)}"
            )
        return list(pembaca)


def _baca_json(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise DataTidakValidError(f"JSON tidak valid: {error}") from error
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise DataTidakValidError("JSON harus berupa list yang berisi object")
    return data


def baca_mentah(path):
    """Baca file .csv atau .json menjadi list of dict (belum divalidasi).

    Raise: FileNotFoundError, DataTidakValidError.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")
    ekstensi = path.suffix.lower()
    try:
        if ekstensi == ".csv":
            return _baca_csv(path)
        if ekstensi == ".json":
            return _baca_json(path)
    except UnicodeDecodeError:
        raise DataTidakValidError("file harus berupa teks UTF-8") from None
    raise DataTidakValidError(
        f"format '{ekstensi}' tidak didukung (gunakan .csv atau .json)"
    )


def muat_barang(path):
    """Baca file lalu validasi tiap baris.

    Return: (valid, ditolak)
        valid   = list dict bersih
        ditolak = list tuple (nomor_data, alasan)
    """
    valid, ditolak = [], []
    for nomor, baris in enumerate(baca_mentah(path), start=1):
        try:
            valid.append(validasi_baris(baris))
        except DataTidakValidError as error:
            ditolak.append((nomor, str(error)))
    return valid, ditolak


def tulis_csv(records, path, kolom):
    """Tulis list of dict ke CSV; folder tujuan dibuat bila belum ada."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        penulis = csv.DictWriter(file, fieldnames=list(kolom))
        penulis.writeheader()
        penulis.writerows(records)
    return path


def tulis_json(data, path):
    """Tulis objek Python ke JSON berindentasi (UTF-8)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    return path
