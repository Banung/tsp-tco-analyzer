import time


class GreedyRouteFinder:
    """
    Algoritma A: Greedy Nearest Neighbor (Heuristik).

    Strategi: Dari posisi saat ini, selalu pilih pelanggan terdekat yang
    belum dikunjungi. Ulangi hingga semua pelanggan selesai, lalu kembali
    ke Hub.

    Kompleksitas Waktu : O(n^2):    untuk setiap n node, scan sisa
                                    (n-1) node untuk mencari node yang terdekat.
                                    Loop luar: n iterasi, loop dalam: O(n) per
                                    iterasi → total O(n^2).
    Kompleksitas Ruang : O(n):      array visited berukuran n + path list
                                    yang meningkat secara linear.
    """

    def __init__(self, distance_matrix, package_weights, fuel_calculator):
        """
        Inisialisasi dengan matriks jarak dan parameter bahan bakar.

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

    # ------------------------------------------------------------------
    # PUBLIC API & INTI ALGORITMA GREEDY
    # ------------------------------------------------------------------

    def solve(self):
        """
        Jalankan algoritma Greedy dan kembalikan hasil murni algoritma.

        Di setiap langkah, kurir memilih node yang belum dikunjungi dengan
        jarak paling dekat dari posisi saat ini. Biaya bensin dihitung
        secara dinamis per-segmen berdasarkan beban paket yang tersisa.

        Returns
        -------
        dict dengan key:
            path              : list[int]   — urutan node termasuk Hub di awal & akhir
            distance_km       : float       — total jarak rute yang dihasilkan (km)
            total_fuel_liters : float       — total bensin yang dikonsumsi seluruh rute (liter)
            segment_fuel      : list[float] — konsumsi bensin per segmen (liter)
            execution_time_ms : float       — waktu komputasi (milidetik)
        """
        start_time = time.perf_counter()

        visited = [False] * self.num_nodes
        visited[0] = True  # Mulai dari Hub (node 0)
        path = [0]
        total_distance = 0.0
        current_node = 0
        customers_visited = 0
        num_customers = self.num_nodes - 1  # Semua node selain Hub

        while customers_visited < num_customers:
            nearest_node = -1
            nearest_distance = float("inf")

            # Cari tetangga terdekat yang belum dikunjungi
            for candidate in range(1, self.num_nodes):  # skip Hub (node 0)
                if not visited[candidate]:
                    dist = self.graph[current_node][candidate]
                    if dist < nearest_distance:
                        nearest_distance = dist
                        nearest_node = candidate

            if nearest_node == -1:  # Jika semua node sudah dikunjungi
                break

            # Mengunjungi node terdekat
            visited[nearest_node] = True
            path.append(nearest_node)
            total_distance += nearest_distance

            # Setelah mengantar paket, beban berkurang (Note: Pengurangan
            # dan perhitungan bensin di-handle oleh fuel_calc di akhir)
            current_node = nearest_node
            customers_visited += 1

        # Kembali ke Hub setelah semuanya selesai
        return_distance = self.graph[current_node][0]
        total_distance += return_distance
        path.append(0)

        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000

        # Menghitung konsumsi bensin menggunakan Utility terpusat
        total_fuel, segment_fuel = self.fuel_calc.calculate_route_fuel(
            path, self.graph, self.package_weights
        )

        return {
            "path": path,
            "distance_km": total_distance,
            "total_fuel_liters": total_fuel,
            "segment_fuel": segment_fuel,
            "execution_time_ms": execution_time_ms,
        }
