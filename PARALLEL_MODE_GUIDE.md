# Parallel Hyperparameter Tuning - Quick Guide

## ⚡ Peningkatan Kecepatan

Script sekarang menggunakan **parallel processing** dengan 2 workers!

### 📊 Perbandingan Kecepatan:

| Mode                 | Workers | Total Configs | Estimasi Waktu |
| -------------------- | ------- | ------------- | -------------- |
| **Sequential**       | 1       | 10,368        | 86-173 jam     |
| **Parallel (2x)** ✅ | 2       | 10,368        | **43-87 jam**  |
| **Parallel (4x)**    | 4       | 10,368        | 22-43 jam      |

**Speed Boost: ~2x lebih cepat!** ⚡

## 🎯 Konfigurasi

Dalam file [`hyperparameter_tuning.py`](hyperparameter_tuning.py), line 44:

```python
NUM_WORKERS = 2  # Default: 2 configs berjalan bersamaan
```

### Opsi Konfigurasi:

```python
# Opsi 1: Sequential (paling lambat, paling stabil)
NUM_WORKERS = 1

# Opsi 2: Parallel 2x (RECOMMENDED) ✅
NUM_WORKERS = 2  # Balance speed & stability

# Opsi 3: Parallel 4x (lebih cepat, perlu CPU kuat)
NUM_WORKERS = 4

# Opsi 4: Auto-detect CPU cores
NUM_WORKERS = cpu_count() - 1  # Sisakan 1 core untuk sistem
```

## 💻 Requirement CPU

### Rekomendasi untuk NUM_WORKERS:

| CPU Cores | RAM    | Recommended Workers    |
| --------- | ------ | ---------------------- |
| 2 cores   | 4-8 GB | **1** (sequential)     |
| 4 cores   | 8 GB   | **2** ✅ (recommended) |
| 6+ cores  | 16+ GB | **3-4** (very fast)    |
| 8+ cores  | 32+ GB | **4-6** (blazing fast) |

### Cek CPU Anda:

```python
from multiprocessing import cpu_count
print(f"CPU cores available: {cpu_count()}")
```

## 🚀 Cara Menggunakan

### 1. Jalankan dengan Default (2 workers):

```bash
python hyperparameter_tuning.py
```

Output:

```
⚡ PARALLEL MODE: Using 2 workers
   Speed boost: ~2x faster than sequential
   Estimated time: 43.2 - 86.4 hours
```

### 2. Custom Workers (Edit File):

Buka [`hyperparameter_tuning.py`](hyperparameter_tuning.py), ubah line 44:

```python
NUM_WORKERS = 4  # Ubah sesuai kebutuhan
```

## 📊 Monitoring

### Output Parallel Mode:

```
⚙️  Config 234/10368 - Starting...
   Pop: 700, Gen: 20, Cross: 0.8, Mut: 0.01
   Elitism: 2, Tournament: 8, 2-Opt: True
================================================================================

⚙️  Config 235/10368 - Starting...
   Pop: 700, Gen: 40, Cross: 0.8, Mut: 0.01
   Elitism: 5, Tournament: 5, 2-Opt: True
================================================================================

✅ Config 234 completed:
   Mean Distance: 15.23 km
   Feasible Rate: 100.0%

✅ Config 235 completed:
   Mean Distance: 15.41 km
   Feasible Rate: 100.0%

📊 Progress: 235/10368 (2.3%)

💾 Checkpoint saved: 235 configs completed
```

### Lihat Task Manager:

- **Windows**: Ctrl+Shift+Esc → Performance → CPU
- **Lihat**: Akan ada 2-4 Python processes berjalan
- **CPU Usage**: ~50-100% (tergantung NUM_WORKERS)

## ⚠️ Troubleshooting

### Masalah 1: "BrokenPipeError" atau "EOFError"

**Penyebab**: Multiprocessing issue di Windows

**Solusi**:

```python
# Sudah ditambahkan di script:
if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
```

### Masalah 2: Laptop Lag / Hang

**Penyebab**: Terlalu banyak workers

**Solusi**: Kurangi NUM_WORKERS

```python
NUM_WORKERS = 1  # Kembali ke sequential
```

### Masalah 3: RAM Penuh

**Penyebab**: Setiap worker butuh memory

**Solusi**:

- Kurangi NUM_WORKERS
- Close aplikasi lain
- Upgrade RAM (jika perlu)

### Masalah 4: "Pool not running"

**Penyebab**: Error di salah satu worker

**Solusi**: Script akan auto-save checkpoint, jalankan ulang

## 🔄 Checkpoint dengan Parallel Mode

### Auto-Save Tetap Aktif:

- ✅ Checkpoint setiap 5 configs (thread-safe)
- ✅ Resume support (detect otomatis)
- ✅ Ctrl+C safe (save sebelum exit)

### Resume Workflow:

```bash
# Jika interrupt atau error
Ctrl+C

# Checkpoint otomatis tersimpan
💾 Checkpoint saved: 150 configs completed

# Jalankan lagi dengan workers yang sama
python hyperparameter_tuning.py

# Output:
✓ Checkpoint found! Loaded 150 completed configs
⚡ PARALLEL MODE: Using 2 workers
🔄 RESUMING from config #151/10368
```

## 💡 Tips Optimasi

### 1. **Optimal Workers = CPU Cores - 1**

```python
from multiprocessing import cpu_count
NUM_WORKERS = max(1, cpu_count() - 1)  # Sisakan 1 core
```

### 2. **Jalankan Saat Laptop Idle**

- Malam hari / tidak digunakan
- Tutup browser & aplikasi berat
- Terhubung ke charger

### 3. **Monitor Resource Usage**

```python
# Windows PowerShell
Get-Process python | Select-Object CPU, WorkingSet
```

### 4. **Batch Processing**

Jika RAM terbatas, proses per batch:

```python
# Process 1000 configs at a time
# Edit script untuk limit configs_to_process[:1000]
```

## 📈 Estimasi Waktu Real

### Dengan NUM_WORKERS = 2:

| Total Configs  | Time per Config | Total Time         |
| -------------- | --------------- | ------------------ |
| 10,368         | 10-20s          | **43-87 jam**      |
| 1,000          | 10-20s          | 4-8 jam            |
| 162 (extended) | 10-20s          | **1.4-2.7 jam** ✅ |

### Untuk Testing Cepat:

Gunakan [`hyperparameter_tuning_extended.py`](hyperparameter_tuning_extended.py):

```bash
python hyperparameter_tuning_extended.py
# Only 162 configs, 2 workers → ~1 jam!
```

## ✅ Kesimpulan

**Parallel Mode Aktif:**

- ✅ **2x lebih cepat** dengan 2 workers
- ✅ **Checkpoint tetap aman** (thread-safe)
- ✅ **Resume support** berfungsi normal
- ✅ **Auto CPU optimization**

**Sekarang:**

- 10,368 configs: **43-87 jam** (vs 86-173 jam)
- 162 configs: **~1 jam** (extended version)

**Cukup jalankan:**

```bash
python hyperparameter_tuning.py
```

Dan biarkan berjalan 2x lebih cepat! 🚀
