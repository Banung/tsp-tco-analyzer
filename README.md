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
- **Kompleksitas Waktu: O(n!) Worst Case | O(b^n) Average Case**
  Tanpa optimasi, DFS menelusuri seluruh permutasi rute `n!`. Namun, kami menerapkan dua lapis pemangkasan cabang (*Pruning* Langsung & *Lower Bound*). Kami juga menggunakan **Greedy Warm-Start** agar batas awal langsung optimal. Efeknya, rata-rata *branching factor* (b) mengecil drastis, mengurangi waktu eksekusi secara signifikan.
- **Kompleksitas Ruang: O(n²)**
  Didominasi oleh matriks pre-komputasi `_sorted_neighbors` berukuran `n × (n-1)` untuk mengurutkan tetangga terdekat. Ini merupakan *trade-off* ruang (memori) demi menghindari *overhead* *sorting* iteratif di dalam rekursi (waktu). Stack rekursi itu sendiri hanya sedalam `O(n)`.

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
