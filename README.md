# tsp-tco-analyzer
Simulasi komputasi untuk mengevaluasi trade-off finansial antara algoritma rute eksak (DFS) dan heuristik (Greedy), membandingkan biaya server cloud dengan efisiensi BBM pada logistik last-mile.

# Analisis Kompleksitas Algoritma B — DFS Backtracking dengan Pruning

> Bagian ini mendokumentasikan **Algoritma B** yang diimplementasikan di `src/algo_exact.py`.
> Algoritma ini bertanggung jawab menemukan rute kurir yang **secara absolut paling optimal**
> (jarak terpendek), dengan cara menelusuri seluruh kemungkinan rute secara sistematis
> dan memangkas cabang yang tidak menjanjikan.

---

## Cara Kerja Singkat

Algoritma memulai penelusuran dari **Hub (Node 0)** dan secara rekursif mengunjungi
semua node pelanggan. Di setiap langkah, ada tiga mekanisme utama:

1. **MAJU (Push)** — Tandai node berikutnya sebagai sudah dikunjungi, masukkan ke jalur saat ini.
2. **REKURSI** — Lanjutkan penelusuran dari node tersebut.
3. **MUNDUR (Backtrack/Pop)** — Batalkan kunjungan, coba pilihan lain.

Ditambah dua lapis **Pruning** untuk memangkas cabang yang tidak perlu:
- **Pruning Langsung**: Potong jika jarak saat ini sudah ≥ rekor terbaik.
- **Pruning Lower Bound**: Potong jika jarak saat ini + estimasi minimum sisa perjalanan ≥ rekor terbaik.

---

## Analisis Kompleksitas Waktu

### Worst Case: **O(n!)**

Penelusuran DFS membangun pohon permutasi dari semua kemungkinan urutan kunjungan.

```
Langkah 1 → n pilihan node berikutnya
Langkah 2 → (n-1) pilihan node berikutnya
Langkah 3 → (n-2) pilihan node berikutnya
...
Langkah n → 1 pilihan tersisa

Total kemungkinan rute = n × (n-1) × (n-2) × ... × 1 = n!
```

Dengan `n = 11` pelanggan (+ 1 Hub = 12 node total), worst case adalah:

```
11! = 39.916.800 kemungkinan rute
```

Ini adalah skenario **tanpa pruning sama sekali** — semua cabang ditelusuri penuh.

### Average Case: **Jauh di bawah O(n!)**

Pruning memotong cabang sedini mungkin, sehingga banyak sub-pohon tidak pernah
ditelusuri. Efektivitasnya bergantung pada kualitas solusi terbaik yang ditemukan lebih
awal — semakin baik solusi awal, semakin agresif pruning memangkas cabang berikutnya.

**Contoh nyata pada kode ini:**

```python
# Pruning Lapis 1: potong langsung jika sudah kalah
if current_distance >= self.best_distance:
    return

# Pruning Lapis 2: potong jika bahkan estimasi terbaik pun tidak cukup
if current_distance + self._lower_bound(visited) >= self.best_distance:
    return
```

`_lower_bound()` menghitung estimasi jarak minimum sisa perjalanan dengan mengambil
edge terkecil dari setiap node yang belum dikunjungi. Ini memastikan bahwa cabang
yang secara matematis tidak mungkin mengalahkan solusi terbaik saat ini langsung
dipangkas, tanpa perlu ditelusuri sampai akhir.

### Ringkasan Kompleksitas Waktu

| Kondisi         | Kompleksitas | Keterangan                                          |
|-----------------|--------------|-----------------------------------------------------|
| Worst Case      | O(n!)        | Pruning tidak pernah memangkas (sangat jarang terjadi) |
| Average Case    | O(b^n)       | b = branching factor efektif setelah pruning, b < n |
| Best Case       | O(n²)        | Solusi optimal ditemukan di awal, hampir semua cabang terpangkas |

> **Catatan:** Meskipun asimptotik tetap O(n!), pruning membuat algoritma ini
> **praktis dijalankan** untuk `n ≤ 12` sebagaimana batasan pada tugas ini.

---

## Analisis Kompleksitas Ruang

### **O(n)**

Penggunaan memori bergantung pada dua struktur utama:

```
1. Call Stack Rekursi
   ├── Kedalaman maksimal = n level (satu per node yang dikunjungi)
   └── Kompleksitas: O(n)

2. Array Pendukung
   ├── visited[]     → ukuran n    → O(n)
   ├── current_path  → maks. n+1  → O(n)
   └── best_path     → maks. n+1  → O(n)

Total Ruang = O(n) + O(n) + O(n) = O(n)
```

Ini adalah keunggulan besar DFS dibanding BFS (Breadth-First Search) yang harus
menyimpan semua node di satu level secara bersamaan — BFS untuk TSP membutuhkan
O(n!) ruang.

### Ringkasan Kompleksitas Ruang

| Struktur Data   | Ukuran   | Keterangan                              |
|-----------------|----------|-----------------------------------------|
| Call stack      | O(n)     | Rekursi maksimal sedalam n level        |
| `visited[]`     | O(n)     | Satu boolean per node                   |
| `current_path`  | O(n)     | Rute yang sedang ditelusuri             |
| `best_path`     | O(n)     | Snapshot rute terbaik yang ditemukan    |
| **Total**       | **O(n)** | Linear terhadap jumlah node             |

---

## Perbandingan dengan Algoritma A (Heuristik Greedy)

| Aspek                    | Algoritma B (DFS + Pruning) | Algoritma A (Greedy)  |
|--------------------------|-----------------------------|-----------------------|
| **Kompleksitas Waktu**   | O(n!) worst case            | O(n²)                 |
| **Kompleksitas Ruang**   | O(n)                        | O(n)                  |
| **Jaminan Optimalitas**  | Selalu rute terpendek       | Tidak dijamin         |
| **Kecepatan**            | Lambat (eksponensial)       | Cepat (kuadratik)     |
| **Biaya Server (TCO)**   | Lebih tinggi                | Sangat rendah         |
| **Cocok untuk**          | n ≤ 12, BBM mahal           | n besar, BBM murah    |

---

## Kesimpulan Teknis

DFS Backtracking dengan Pruning adalah pilihan yang tepat untuk **Algoritma B** karena:

1. **Correctness terjamin** — menelusuri seluruh ruang solusi secara sistematis,
   tidak ada rute optimal yang terlewat.
2. **Pruning mengontrol biaya server** — tanpa pruning, algoritma ini tidak praktis
   bahkan untuk `n = 10`. Dengan dua lapis pruning, waktu eksekusi turun drastis.
3. **Skala tugas sesuai** — untuk `n ≤ 12` sebagaimana spesifikasi tugas, algoritma
   ini masih dapat selesai dalam hitungan milidetik hingga detik, sehingga perbandingan
   TCO dengan Algoritma A tetap bermakna secara bisnis.