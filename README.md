# TSP TCO Analyzer: Last-Mile Delivery Cost Simulation

Simulasi komputasi untuk mengevaluasi *trade-off* finansial antara algoritma rute eksak (DFS dengan Pruning) dan heuristik (Greedy). Proyek ini membandingkan Biaya Server Cloud (*Pay-as-you-go*) dengan efisiensi BBM (Logistik *Last-Mile*) di bawah skenario ekonomi yang berbeda.

---

## 1. Cara Menjalankan Program

Program ini berjalan melalui *Command Line Interface* (CLI) dan menerima argumen dinamis untuk memilih skenario ekonomi (berdasarkan file `data/data.json`).

**Persyaratan:**
- Python 3.8+ (Hanya menggunakan *built-in library*)

**Langkah Eksekusi:**
1. Clone repositori ini dan masuk ke direktori utama.
2. Jalankan perintah berikut di terminal:

Untuk Skenario Subsidi (Harga BBM Murah):
```bash
python src/main.py --scenario subsidi
```

Untuk Skenario Krisis (Harga BBM Mahal):
```bash
python src/main.py --scenario krisis
```

---

## 2. Pemilihan Algoritma (Trade-off)

Dalam simulasi ini, kami mengimplementasikan dan membandingkan dua arsitektur algoritma pencarian rute:

1. **Algoritma A (Heuristik - Greedy Nearest Neighbor):** Dipilih karena kecepatan eksekusinya yang instan. Algoritma ini memprioritaskan titik terdekat dari lokasi saat ini.
   * **Trade-off:** Menghasilkan biaya server yang nyaris Rp 0, namun sering terjebak di *local optima*. Rute yang dihasilkan lebih panjang, sehingga operasional memboroskan banyak bahan bakar.
2. **Algoritma B (Eksak - DFS Backtracking with Pruning):** Dipilih untuk mendapatkan jarak absolut terpendek.
   * **Trade-off:** Menjamin efisiensi bahan bakar paling maksimal, namun membebani komputasi secara eksponensial. Tagihan server *cloud* dapat membengkak secara signifikan.

---

## 3. Analisis Kompleksitas (Big-O)

### A. Algoritma A (Greedy Nearest Neighbor)
- **Kompleksitas Waktu: O(n²)**
  Greedy melakukan iterasi satu per satu untuk setiap node yang belum dikunjungi. Pada setiap langkah, program mengecek semua kandidat yang tersisa untuk menemukan jarak terdekat. Total pencarian menurun secara linear `(n-1) + (n-2) + ... + 1 = O(n²)`.
- **Kompleksitas Ruang: O(n)**
  Hanya menggunakan array pendukung linear seperti `visited[]`, `path`, dan variabel *tracking* untuk *dynamic fuel cost*.

### B. Algoritma B (DFS Backtracking dengan Pruning)

**Implementasi:** `src/algo_exact.py` — class `ExactRouteFinder`

#### Cara Kerja
Algoritma menelusuri seluruh kemungkinan urutan kunjungan secara rekursif mulai dari
Hub (node 0), dengan tiga mekanisme dasar backtracking: **MAJU** (tandai node sebagai
dikunjungi, tambahkan ke jalur), **REKURSI** (lanjutkan dari node tersebut), **MUNDUR**
(batalkan kunjungan, coba cabang lain). Tujuannya murni mencari **jarak total (km)
terpendek**.

Tiga optimasi diterapkan agar performa praktis untuk `n ≤ 12`:

1. **Pruning Dua Lapis**
   - *Pruning Langsung*: cabang dipotong jika `current_distance ≥ best_distance`.
   - *Pruning Lower Bound*: cabang dipotong jika `current_distance + estimasi_sisa ≥ best_distance`,
     di mana estimasi sisa dihitung oleh `_lower_bound()` — mengambil edge terpendek dari
     setiap node yang belum dikunjungi *menuju node lain yang juga belum dikunjungi atau
     ke Hub*. Edge ke node yang sudah selesai dikunjungi sengaja diabaikan karena jalur
     itu tidak mungkin lagi ditempuh — ini membuat estimasi lebih ketat dan pruning lebih
     sering aktif dibanding pendekatan naif.

2. **Greedy Warm-Start** — Sebelum DFS berjalan, `solve()` memanggil `GreedyRouteFinder`
   terlebih dahulu untuk mendapatkan solusi awal yang langsung di-set sebagai `best_distance`.
   Dengan begini, pruning sudah aktif sejak percabangan pertama, bukan menunggu DFS
   menemukan solusi layak secara organik. Pendekatan ini juga menghindari duplikasi logika
   "cari tetangga terdekat" di dua tempat berbeda.

3. **Nearest-First Traversal + Precompute `_sorted_neighbors`** — Setiap node menelusuri
   tetangganya dalam urutan jarak terdekat dahulu (bukan urutan index di JSON), sehingga
   solusi mendekati optimal cenderung ditemukan lebih awal dan `best_distance` mengecil
   lebih cepat. Urutan ini dihitung sekali saat `__init__` dan disimpan di
   `_sorted_neighbors`, menghindari pengurutan ulang yang mahal di setiap pemanggilan rekursi.

- **Kompleksitas Waktu: O(n!) Worst Case | jauh lebih cepat secara praktis**
  Tanpa pruning, DFS menelusuri seluruh `n!` permutasi rute. Dengan dua lapis pruning +
  warm-start, branching factor efektif mengecil drastis. Pada data nyata (12 node),
  waktu eksekusi terukur sekitar **500–600 ms** — jauh di bawah worst case teoritis,
  tapi tetap jauh lebih mahal dibanding Greedy yang hanya butuh hitungan puluhan mikrodetik.

- **Kompleksitas Ruang: O(n²)**
  Didominasi oleh `_sorted_neighbors` (matriks `n × (n-1)`, dibuat sekali di `__init__`).
  Struktur pendukung lain (`visited[]`, `current_path`, `best_path`, stack rekursi)
  masing-masing O(n). Ini trade-off ruang yang disengaja: membayar O(n²) memori sekali
  demi menghindari overhead sorting berulang selama rekursi berjalan.

#### Catatan Penting: Jarak Optimal ≠ Bensin Optimal
Karena `_dfs_pruning` mengoptimalkan **jarak (km)**, bukan **konsumsi bensin (liter)**,
rute tependek yang ditemukan belum tentu paling hemat bahan bakar. Urutan kunjungan
memengaruhi *kapan* beban berat dibawa — mengantar paket berat di awal rute (saat motor
masih penuh dan boros) vs di akhir (saat motor sudah ringan dan irit) menghasilkan total
bensin yang berbeda meski jarak tempuhnya sama. Bensin baru dihitung oleh `FuelCalculator`
**setelah** rute eksak final didapat, bukan sebagai bagian dari fungsi pruning DFS itu
sendiri.

---

## 4. Summary: Kesimpulan Bisnis & Titik Break-Even

*Skenario yang diuji menggunakan 1 Hub dan 11 pelanggan nyata.*

Berdasarkan simulasi, **Skenario Subsidi (Rp 5.000/L)** memenangkan pemakaian **Algoritma Greedy**. Karena bensin murah, perusahaan tidak perlu membayar mahal untuk server demi menghemat sedikit liter bensin. Sebaliknya, pada **Skenario Krisis (Rp 20.000/L)**, penghematan bahan bakar yang ditawarkan oleh rute optimal **Algoritma Eksak** berhasil menutupi mahalnya tagihan komputasi server.

### Perhitungan Titik Break-Even (BEP)
Untuk menentukan kapan manajemen harus beralih (migrasi) dari sistem Greedy ke DFS, kita harus mencari titik harga bensin di mana **Total Cost of Ownership (TCO) Algoritma A sama dengan Algoritma B**.

Berdasarkan log eksekusi, didapatkan selisih performa berikut:
- **Selisih Waktu Komputasi Server:** `589.0106` ms *(Setara dengan Rp 29.450)*
- **Selisih Efisiensi BBM:** Algoritma Eksak lebih hemat `0.24` Liter.

**Formula BEP:**
`(Selisih Liter Bensin × Harga BEP) = Selisih Biaya Server`
`Harga BEP = Selisih Biaya Server / Selisih Liter Bensin`

**Kesimpulan Akhir:**
Algoritma Eksak (DFS) baru mulai memberikan keuntungan finansial (masuk akal secara ekonomi) jika harga BBM di pasar menyentuh angka **Rp 122.710 / Liter**. Jika harga bensin di bawah angka tersebut, perusahaan diwajibkan tetap memakai Algoritma Greedy.
