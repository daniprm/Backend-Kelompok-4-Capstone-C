# Hyperparameter Tuning dengan Checkpoint - Quick Guide

## ✅ Fitur yang Sudah Ditambahkan

1. **Checkpoint Auto-Save**: Otomatis save setiap 5 konfigurasi
2. **Resume Support**: Bisa melanjutkan dari titik terakhir jika terhenti
3. **Sleep Prevention**: Mencegah laptop sleep selama proses berjalan
4. **Error Handling**: Tetap save checkpoint jika ada error

## 🚀 Cara Menggunakan

### 1. Jalankan Pertama Kali

```bash
python hyperparameter_tuning.py
```

Output:

```
================================================================================
HYPERPARAMETER TUNING - HYBRID GENETIC ALGORITHM (WITH CHECKPOINTS)
================================================================================
Loading destinations data...
Loaded 50 destinations

🆕 Starting fresh (no checkpoint found)

Total configurations: 10368
Runs per configuration: 3
Total experiments: 31104
Estimated time: 86.4 - 172.8 hours

Press Enter to START tuning (or Ctrl+C to cancel)...
```

### 2. Jika Proses Terhenti (Sleep/Shutdown/Error)

**Proses akan otomatis save checkpoint setiap 5 konfigurasi**

File checkpoint: `tuning_checkpoint.pkl`

### 3. Resume dari Checkpoint

```bash
# Jalankan script yang sama lagi
python hyperparameter_tuning.py
```

Output:

```
✓ Checkpoint found! Loaded 25 completed configs
  Last saved: 2025-12-19T14:30:45.123456
  Last config: #25

🔄 RESUMING from config #26/10368
   Progress: 25/10368 configs completed
   Remaining: 10343 configs

Press Enter to RESUME tuning (or Ctrl+C to cancel)...
```

## 🛑 Cara Menghentikan dengan Aman

### Opsi 1: Tekan Ctrl+C

```
⚠️  Interrupted by user - saving checkpoint...
💾 Checkpoint saved: 42 configs completed (Config #42)

💡 To resume: Just run the script again!
   Checkpoint saved in: tuning_checkpoint.pkl
```

### Opsi 2: Tutup Terminal

- Checkpoint terakhir sudah tersimpan
- Jalankan lagi untuk resume

### Opsi 3: Laptop Kehabisan Baterai

- Checkpoint terakhir (setiap 5 configs) sudah tersimpan
- Jalankan lagi untuk resume

## 📊 Monitoring Progress

### 1. Lihat Output Terminal

```
Configuration 45/10368
Completed: 44/10368 (0.4%)
```

### 2. Cek File Checkpoint

```powershell
# PowerShell
Test-Path tuning_checkpoint.pkl  # True = ada checkpoint
(Get-Item tuning_checkpoint.pkl).LastWriteTime  # Waktu terakhir save
```

### 3. Cek File CSV (Jika Ada)

```powershell
# Hitung jumlah hasil yang sudah tersimpan
(Import-Csv hyperparameter_tuning_detailed_*.csv | Measure-Object).Count
```

## 🎯 Tips Penggunaan

### 1. **Jangan Khawatir Tentang Sleep Mode**

- Script otomatis disable sleep mode Windows
- Laptop tidak akan sleep selama proses jalan
- Sleep mode di-enable kembali setelah selesai

### 2. **Checkpoint Otomatis Setiap 5 Configs**

- Config #5, #10, #15, #20, dst
- Maksimal kehilangan progress: 4 configs (~12-15 runs)

### 3. **Jalankan Saat Tidak Digunakan**

- Malam hari / saat tidur
- Pastikan laptop terhubung charger
- Tutup aplikasi lain yang berat

### 4. **Monitor via Remote Desktop (Optional)**

- Bisa monitor dari HP/laptop lain
- Gunakan Windows Remote Desktop
- Atau TeamViewer / AnyDesk

## ⚠️ Troubleshooting

### Masalah 1: "Cannot open checkpoint file"

```bash
# Hapus checkpoint corrupt
del tuning_checkpoint.pkl
# Mulai dari awal
python hyperparameter_tuning.py
```

### Masalah 2: "Sleep mode tidak ter-disable"

- Buka Control Panel → Power Options
- Manually set "Put computer to sleep" → **Never**
- Jalankan script sebagai Administrator

### Masalah 3: "Script berhenti tiba-tiba"

- Cek apakah ada error di terminal
- Jalankan lagi, script akan resume otomatis
- Checkpoint terakhir sudah tersimpan

### Masalah 4: "Progress terlalu lambat"

**Opsi A**: Gunakan extended tuning (lebih cepat)

```bash
python hyperparameter_tuning_extended.py  # 2 jam saja
```

**Opsi B**: Kurangi NUM_RUNS_PER_CONFIG
Edit file, ubah:

```python
NUM_RUNS_PER_CONFIG = 3  # Ubah jadi 2 untuk lebih cepat
```

## 📁 File Output

### Saat Proses Berjalan:

- `tuning_checkpoint.pkl` - Checkpoint untuk resume

### Setelah Selesai:

- `hyperparameter_tuning_detailed_YYYYMMDD_HHMMSS.csv`
- `hyperparameter_tuning_aggregated_YYYYMMDD_HHMMSS.csv`
- `hyperparameter_tuning_full_YYYYMMDD_HHMMSS.json`
- `tuning_checkpoint.pkl` - Otomatis terhapus setelah selesai

## 🔄 Contoh Workflow

### Day 1 - 18:00

```bash
python hyperparameter_tuning.py
# Jalankan, biarkan overnight
```

### Day 2 - 08:00

```
# Bangun pagi, cek progress
Configuration 150/10368
Completed: 149/10368 (1.4%)

# Tekan Ctrl+C untuk stop (jika perlu pakai laptop)
⚠️  Interrupted by user - saving checkpoint...
💾 Checkpoint saved: 149 configs completed
```

### Day 2 - 22:00

```bash
# Malam hari, resume lagi
python hyperparameter_tuning.py

✓ Checkpoint found! Loaded 149 completed configs
🔄 RESUMING from config #150/10368

# Tekan Enter untuk lanjut
```

### Day 7

```
🎉 TUNING COMPLETED!
Total configurations tested: 10368/10368
Total time: 156.30 hours

✓ Checkpoint file removed (tuning completed successfully)
```

## 💡 Rekomendasi

**Untuk hasil lebih cepat:**

1. **Gunakan Extended Tuning** (2 jam):

   ```bash
   python hyperparameter_tuning_extended.py
   ```

2. **Atau kurangi parameter grid** di `hyperparameter_tuning.py`:
   ```python
   PARAMETER_GRID = {
       'population_size': [300, 700],  # Kurangi dari 4 jadi 2
       'generations': [20, 40],         # Kurangi dari 3 jadi 2
       'crossover_rate': [0.7, 0.8],    # Kurangi dari 4 jadi 2
       'mutation_rate': [0.01, 0.05],   # Kurangi dari 4 jadi 2
       'use_2opt': [True],              # Hanya True
       'elitism_count': [2, 5],         # Kurangi dari 3 jadi 2
       'tournament_size': [5, 8],       # Kurangi dari 3 jadi 2
       'two_opt_iterations': [100, 500] # Kurangi dari 3 jadi 2
   }
   # Total: 2×2×2×2×1×2×2×2 = 128 configs (vs 10,368)
   # Time: ~1-2 jam (vs 86-173 jam)
   ```

## ✅ Kesimpulan

Sekarang script sudah:

- ✅ **Auto-save checkpoint** setiap 5 configs
- ✅ **Resume otomatis** jika dijalankan lagi
- ✅ **Prevent sleep mode** Windows
- ✅ **Error handling** yang baik
- ✅ **Progress tracking** yang jelas

**Anda bisa dengan aman:**

- Stop kapan saja dengan Ctrl+C
- Sleep/shutdown laptop
- Resume dari checkpoint kapan saja

**Tinggal jalankan:**

```bash
python hyperparameter_tuning.py
```

Dan biarkan berjalan! 🚀
