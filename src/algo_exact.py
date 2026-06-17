import sys
import time

from greedy import GreedyRouteFinder


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

    def __init__(self, distance_matrix, package_weights, fuel_calculator):
        """
        Inisialisasi dengan matriks jarak (adjacency matrix berbobot).

        Parameters
        ----------
        distance_matrix : list[list[float]]
            Matriks n×n. Baris/kolom 0 = Hub (Gudang Pusat).
            distance_matrix[i][j] = jarak (km) dari node i ke node j.
        package_weights : list[float]
            package_weights = berat paket per node (kg).
        fuel_calculator : FuelCalculator
            Modul utility (terpusat) untuk menghitung konsumsi bensin.
        """
        self.graph = distance_matrix
        self.num_nodes = len(distance_matrix)
        self.package_weights = package_weights
        self.fuel_calc = fuel_calculator

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
                key=lambda j: self.graph[i][j],
            )
            self._sorted_neighbors.append(neighbors)

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
        for node in range(1, self.num_nodes):  # skip Hub (node 0)
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

    def _dfs_pruning(
        self, current_node, visited_count, current_distance, current_path, visited
    ):
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
            return_distance = self.graph[current_node][0]  # balik ke Hub
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
            total_fuel_liters : float      — total bensin yang dikonsumsi seluruh rute (liter)
            segment_fuel      : list[float]— konsumsi bensin per segmen (liter)
            execution_time_ms : float      — waktu komputasi (milidetik)
        """
        # Reset state agar solve() bisa dipanggil ulang pada instance yang sama
        self.best_path = []
        self.best_distance = sys.maxsize

        start_time = time.perf_counter()

        # Warm-start: set rekor awal dari solusi greedy agar pruning
        # langsung aktif sejak DFS pertama kali berjalan.
        # Menghindari duplikasi kode dengan memakai GreedyRouteFinder.
        greedy_solver = GreedyRouteFinder(
            self.graph, self.package_weights, self.fuel_calc
        )
        greedy_res = greedy_solver.solve()

        self.best_distance = greedy_res["distance_km"]
        self.best_path = greedy_res["path"]

        visited = [False] * self.num_nodes
        visited[0] = True  # Mulai dari Hub (node 0)

        self._dfs_pruning(
            current_node=0,
            visited_count=1,
            current_distance=0,
            current_path=[0],
            visited=visited,
        )

        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000

        # SIMULASI BENSIN SETELAH RUTE EKSAK DITEMUKAN
        total_fuel, segment_fuel = self.fuel_calc.calculate_route_fuel(
            self.best_path, self.graph, self.package_weights
        )

        return {
            "path": self.best_path,
            "distance_km": self.best_distance,
            "total_fuel_liters": total_fuel,
            "segment_fuel": segment_fuel,
            "execution_time_ms": execution_time_ms,
        }
