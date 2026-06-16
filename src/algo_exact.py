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

    # ------------------------------------------------------------------
    # PRUNING HELPER
    # ------------------------------------------------------------------

    def _lower_bound(self, visited):
        """
        Estimasi jarak minimum yang tersisa dari node-node yang belum
        dikunjungi. Digunakan untuk pruning lebih agresif.

        Untuk setiap node yang belum dikunjungi, ambil edge terkecilnya
        ke node manapun (termasuk Hub). Jumlah ini adalah lower bound
        jarak yang masih harus ditempuh.

        Kompleksitas: O(n^2) dipanggil tiap node — bisa dioptimalkan
        lebih lanjut dengan precompute, tapi cukup untuk n ≤ 12.
        """
        lb = 0
        for node in range(1, self.num_nodes):   # skip Hub (node 0)
            if not visited[node]:
                min_edge = min(
                    self.graph[node][j]
                    for j in range(self.num_nodes)
                    if j != node
                )
                lb += min_edge
        return lb

    # ------------------------------------------------------------------
    # CORE DFS
    # ------------------------------------------------------------------

    def _dfs_pruning(self, current_node, visited_count, current_distance,
                     current_path, visited):
        """
        Rekursi DFS dengan dua lapis pruning:
          1. Pruning langsung  — potong jika current_distance ≥ best.
          2. Pruning lower bound — potong jika current + estimasi_sisa ≥ best.
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

        # ── RECURSIVE CASE: eksplorasi ke node berikutnya ──
        for next_node in range(1, self.num_nodes):  # range dari 1: skip Hub
            if not visited[next_node]:
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
            path           : list[int]  — urutan node termasuk Hub di awal & akhir
            distance_km    : float      — total jarak rute terpendek (km)
            execution_time_ms : float   — waktu komputasi (milidetik)
        """
        # Reset state agar solve() bisa dipanggil ulang pada instance yang sama
        self.best_path = []
        self.best_distance = sys.maxsize

        start_time = time.perf_counter()

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
# BLOK PENGUJIAN LOKAL (MOCK DATA)
# ======================================================================
if __name__ == "__main__":
    # Dummy 4-node: Hub (0) + 3 pelanggan
    dummy_matrix = [
        [0, 10, 15, 20],
        [10,  0, 35, 25],
        [15, 35,  0, 30],
        [20, 25, 30,  0],
    ]

    finder = ExactRouteFinder(dummy_matrix)
    hasil = finder.solve()

    print("=== HASIL ALGORITMA EKSAK ===")
    print(f"Rute Terbaik  : {' -> '.join(map(str, hasil['path']))}")
    print(f"Jarak Termurah: {hasil['distance_km']} km")
    print(f"Waktu Eksekusi: {hasil['execution_time_ms']:.4f} ms")