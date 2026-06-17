import sys
import time


class ExactRouteFinder:
    """
    Algoritma B: DFS Backtracking dengan Pruning.

    Kompleksitas Waktu : O(n!) worst case — ada n pilihan di langkah pertama,
                         (n-1) di langkah kedua, dst. Pruning memotong cabang
                         yang sudah pasti lebih buruk dari solusi terbaik saat
                         ini, sehingga rata-rata jauh lebih cepat meski
                         asimptotik tetap O(n!).
    Kompleksitas Ruang : O(n) — stack rekursi sedalam n level + array visited.
    """

    def __init__(self, distance_matrix):
        """
        Inisialisasi dengan matriks jarak (adjacency matrix berbobot).

        Parameters
        ----------
        distance_matrix : list[list[float]]
            Matriks n×n. Baris/kolom 0 = Hub (Gudang Pusat).
            distance_matrix[i][j] = jarak (km) dari node i ke node j.
        """
        self.graph = distance_matrix
        self.num_nodes = len(distance_matrix)

        # Rekor rute & jarak terbaik (km)
        self.best_path = []
        self.best_distance = sys.maxsize

        # Precompute: urutan tetangga terdekat per node (ascending distance).
        # Digunakan agar DFS selalu menjajaki node terdekat lebih dulu,
        # sehingga solusi bagus ditemukan lebih awal dan pruning lebih sering aktif.
        self._sorted_neighbors = []
        for i in range(self.num_nodes):
            neighbors = sorted(
                (j for j in range(self.num_nodes) if j != i),
                key=lambda j: self.graph[i][j]
            )
            self._sorted_neighbors.append(neighbors)

    # ------------------------------------------------------------------
    # WARM-START HELPER
    # ------------------------------------------------------------------

    def _greedy_nearest_neighbor(self):
        """
        Heuristik Greedy Nearest Neighbor untuk menghasilkan solusi awal.
        Solusi ini di-set sebagai best_distance sebelum DFS dimulai,
        sehingga pruning langsung aktif sejak iterasi pertama.
        Kompleksitas: O(n²).
        """
        visited = [False] * self.num_nodes
        visited[0] = True
        path = [0]
        dist = 0.0
        cur = 0

        for _ in range(self.num_nodes - 1):
            # Ambil tetangga terdekat yang belum dikunjungi
            for nxt in self._sorted_neighbors[cur]:
                if not visited[nxt]:
                    visited[nxt] = True
                    path.append(nxt)
                    dist += self.graph[cur][nxt]
                    cur = nxt
                    break

        dist += self.graph[cur][0]
        path.append(0)
        return path, dist

    # ------------------------------------------------------------------
    # PRUNING HELPER
    # ------------------------------------------------------------------

    def _lower_bound(self, visited):
        """
        Estimasi jarak minimum yang tersisa dari semua node yang belum dikunjungi.
        Digunakan untuk pruning lebih agresif (Pruning Lapis 2).

        Untuk setiap node yang belum dikunjungi, ambil edge terpendeknya
        ke node lain yang juga belum dikunjungi ATAU ke Hub (node 0).
        Ini memastikan lower bound hanya menghitung edge yang masih mungkin
        ditempuh, bukan edge ke node yang sudah selesai dikunjungi.

        Kompleksitas: O(n) per pemanggilan — memanfaatkan _sorted_neighbors
        yang sudah diurutkan, sehingga cukup ambil elemen pertama yang valid.
        """
        lb = 0.0
        for node in range(1, self.num_nodes):   # skip Hub (node 0)
            if not visited[node]:
                # Ambil edge terpendek ke node yang belum dikunjungi atau ke Hub
                for j in self._sorted_neighbors[node]:
                    if not visited[j] or j == 0:
                        lb += self.graph[node][j]
                        break
        return lb

    # ------------------------------------------------------------------
    # CORE DFS
    # ------------------------------------------------------------------

    def _dfs_pruning(self, current_node, visited_count, current_distance,
                     current_path, visited):
        """
        Rekursi DFS dengan dua lapis pruning:
          1. Pruning langsung   — potong jika current_distance ≥ best.
          2. Pruning lower bound — potong jika current + estimasi_sisa ≥ best.
        Node ditelusuri dalam urutan terdekat-lebih-dulu (nearest-first)
        agar solusi bagus ditemukan sedini mungkin.
        """
        # ── PRUNING LAPIS 1: jarak saat ini sudah tidak mungkin menang ──
        if current_distance >= self.best_distance:
            return

        # ── PRUNING LAPIS 2: bahkan jika sisa perjalanan seoptimal mungkin
        #    pun, total tidak akan mengalahkan rekor saat ini ──
        if current_distance + self._lower_bound(visited) >= self.best_distance:
            return

        # ── BASE CASE: semua pelanggan sudah dikunjungi ──
        if visited_count == self.num_nodes:
            return_distance = self.graph[current_node][0]   # balik ke Hub
            total_distance = current_distance + return_distance
            if total_distance < self.best_distance:
                self.best_distance = total_distance
                self.best_path = current_path.copy() + [0]
            return

        # ── RECURSIVE CASE: eksplorasi ke node berikutnya (nearest-first) ──
        for next_node in self._sorted_neighbors[current_node]:
            if next_node != 0 and not visited[next_node]:  # skip Hub
                travel_distance = self.graph[current_node][next_node]

                # MAJU (Push)
                visited[next_node] = True
                current_path.append(next_node)

                # REKURSI
                self._dfs_pruning(
                    next_node,
                    visited_count + 1,
                    current_distance + travel_distance,
                    current_path,
                    visited,
                )

                # MUNDUR (Backtrack / Pop)
                current_path.pop()
                visited[next_node] = False

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def solve(self):
        """
        Jalankan DFS dan kembalikan hasil murni algoritma.

        Returns
        -------
        dict dengan key:
            path              : list[int]  — urutan node termasuk Hub di awal & akhir
            distance_km       : float      — total jarak rute terpendek (km)
            execution_time_ms : float      — waktu komputasi (milidetik)
        """
        # Reset state agar solve() bisa dipanggil ulang pada instance yang sama
        self.best_path = []
        self.best_distance = sys.maxsize

        start_time = time.perf_counter()

        # Warm-start: set rekor awal dari solusi greedy agar pruning
        # langsung aktif sejak DFS pertama kali berjalan
        warmstart_path, warmstart_dist = self._greedy_nearest_neighbor()
        self.best_path = warmstart_path
        self.best_distance = warmstart_dist

        visited = [False] * self.num_nodes
        visited[0] = True   # Mulai dari Hub (node 0)

        self._dfs_pruning(
            current_node=0,
            visited_count=1,
            current_distance=0,
            current_path=[0],
            visited=visited,
        )

        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000

        return {
            "path": self.best_path,
            "distance_km": self.best_distance,
            "execution_time_ms": execution_time_ms,
        }


# ======================================================================
# BLOK PENGUJIAN LOKAL (MENGGUNAKAN DATA.JSON)
# ======================================================================
if __name__ == "__main__":
    import json
    import os

    # 1. Path ke file data.json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'data', 'data.json')

    # 2. Baca file JSON
    with open(json_path, 'r') as file:
        dataset = json.load(file)

    graph_data = dataset['graph_data']

    # 3. Ambil daftar nama lokasi dan pastikan Gudang Pusat ada di index 0
    node_names = list(graph_data.keys())
    hub_name = "Gudang Pusat Sukamaju"

    if node_names[0] != hub_name:
        node_names.remove(hub_name)
        node_names.insert(0, hub_name)

    num_nodes = len(node_names)

    # 4. Bangun Matriks Ketetanggaan (Distance Matrix) 2D
    real_matrix = [[0.0] * num_nodes for _ in range(num_nodes)]

    for i in range(num_nodes):
        origin = node_names[i]
        for j in range(num_nodes):
            dest = node_names[j]
            if i != j:
                real_matrix[i][j] = graph_data[origin]['distances'][dest]

    # 5. Eksekusi Algoritma dengan Data Asli
    print(f"Memulai komputasi untuk {num_nodes} titik lokasi...")
    finder = ExactRouteFinder(real_matrix)
    hasil = finder.solve()

    # 6. Tampilkan Hasil
    print("\n=== HASIL ALGORITMA EKSAK (REAL DATA) ===")
    print(f"Jarak Termurah: {hasil['distance_km']:.3f} km")
    print(f"Waktu Eksekusi: {hasil['execution_time_ms']:.4f} ms")

    print("\nRute Perjalanan:")
    for step, node_index in enumerate(hasil['path']):
        print(f"  {step + 1}. {node_names[node_index]}")