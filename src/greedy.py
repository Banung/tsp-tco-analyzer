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

    def __init__(self, distance_matrix, package_weights,
                 fuel_full, fuel_empty):
        """
        Inisialisasi dengan matriks jarak dan parameter bahan bakar.

        Parameters
        ----------
        distance_matrix : list[list[float]]
            Matriks n×n. Baris/kolom 0 = Hub (Gudang Pusat).
            distance_matrix[i][j] = jarak (km) dari node i ke node j.
        package_weights : list[float]
            package_weights = berat paket per node (kg).
        fuel_full : float
            fuel_full = konsumsi bensin (liter/km) saat motor membawa beban penuh.
        fuel_empty : float
            fuel_empty = konsumsi bensin (liter/km) saat motor tidak membawa beban (kosong).
        """
        self.graph = distance_matrix
        self.num_nodes = len(distance_matrix)
        self.package_weights = package_weights
        self.fuel_full = fuel_full       
        self.fuel_empty = fuel_empty

        # Total berat semua paket yang dibawa di awal perjalanan
        self.total_initial_weight = sum(package_weights)

    # ------------------------------------------------------------------
    # FUEL RATIO HELPER
    # ------------------------------------------------------------------

    def get_fuel_ratio(self, current_load):
        """
        Hitung rasio konsumsi bensin (liter/km) berdasarkan beban saat ini.

        Parameters
        ----------
        current_load : float
            current_float = total berat paket yang masih dibawa kurir (kg).

        Returns
        -------
        float
            Rasio konsumsi bensin (liter/km).
        """
        if self.total_initial_weight == 0:
            return self.fuel_empty

        load_ratio = current_load/self.total_initial_weight
        return self.fuel_empty+load_ratio*(self.fuel_full-self.fuel_empty)

    # ------------------------------------------------------------------
    # INTI ALGORITMA GREEDY
    # ------------------------------------------------------------------

    def greedy_search(self):
        """
        Proses pencarian rute dengan strategi Nearest Neighbor.

        Di setiap langkah, kurir memilih node yang belum dikunjungi dengan
        jarak paling dekat dari posisi saat ini. Biaya bensin dihitung
        secara dinamis per-segmen berdasarkan beban paket yang tersisa
        setelah setiap pengantaran.

        Returns
        -------
        tuple[list[int], float, list[float]]
            path = urutan node yang dikunjungi (termasuk Hub di awal & akhir)
            total_distance = total jarak rute (km)
            segment_fuel = konsumsi bensin per segmen (liter)
        """
        visited = [False]*self.num_nodes
        visited[0] = True  # Mulai dari Hub (node 0)
        path = [0]
        total_distance = 0.0
        segment_fuel = []
        current_node = 0
        current_load = self.total_initial_weight  # Mulai penuh
        customers_visited = 0
        num_customers = self.num_nodes-1  # Semua node selain Hub

        while customers_visited < num_customers:
            nearest_node = -1
            nearest_distance = float('inf')

            # Cari tetangga terdekat yang belum dikunjungi
            for candidate in range(1, self.num_nodes):  # skip Hub (node 0)
                if not visited[candidate]:
                    dist = self.graph[current_node][candidate]
                    if dist < nearest_distance:
                        nearest_distance = dist
                        nearest_node = candidate

            if nearest_node == -1:  # Jika semua node sudah dikunjungi
                break

            # Hitung konsumsi bensin segmen saat ini sebelum mengantar paket, kurir masih membawa current_load saat menempuh jarak ini
            fuel_ratio = self.get_fuel_ratio(current_load)
            fuel_used = nearest_distance*fuel_ratio
            segment_fuel.append(fuel_used)

            # Mengunjungi node terdekat
            visited[nearest_node] = True
            path.append(nearest_node)
            total_distance += nearest_distance

            # Setelah mengantar paket, beban berkurang
            current_load -= self.package_weights[nearest_node]
            current_load = max(0.0, current_load)  # Muatan tidak boleh negatif
            current_node = nearest_node
            customers_visited += 1

        # Kembali ke Hub setelah semuanya selesai
        return_distance = self.graph[current_node][0]
        fuel_ratio = self.get_fuel_ratio(current_load)  # Muatan sisa
        fuel_used = return_distance*fuel_ratio
        segment_fuel.append(fuel_used)
        total_distance += return_distance
        path.append(0)

        return path, total_distance, segment_fuel

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def solve(self):
        """
        Jalankan algoritma Greedy dan kembalikan hasil murni algoritma.

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
        path, total_distance, segment_fuel = self.greedy_search()
        end_time = time.perf_counter()
        execution_time_ms = (end_time-start_time) * 1000
        return {
            "path": path,
            "distance_km": total_distance,
            "total_fuel_liters": sum(segment_fuel),
            "segment_fuel": segment_fuel,
            "execution_time_ms": execution_time_ms,
        }


# ======================================================================
# PARSER DATA.JSON
# ======================================================================

def load_graph_from_json(json_path):
    """
    Urutan node: index 0 selalu Hub (Gudang Pusat), index 1 hingga n adalah
    pelanggan sesuai urutan kemunculan di file data.json.

    Parameters
    ----------
    json_path : str
        Path ke file data.json.

    Returns
    -------
    tuple[list[str], list[list[float]], list[float], dict]
        node_names = nama lokasi per index
        distance_matrix = matriks n×n jarak (km)
        package_weights = berat paket per node (kg)
        config = dict config (fuel, server cost, scenarios)
    """
    import json
    import os

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File tidak ditemukan: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    config     = raw["config"]
    graph_data = raw["graph_data"]

    # Menyusun urutan node: Hub di index 0, sisanya index 1 ~ n
    all_names  = list(graph_data.keys())
    hub_name   = all_names[0]
    node_names = [hub_name]+[n for n in all_names if n != hub_name]
    n = len(node_names)
    name_to_idx = {name: i for i, name in enumerate(node_names)}

    # Membangun adjacency matrix n×n
    distance_matrix = [[0.0]*n for _ in range(n)]
    for src_name, data in graph_data.items():
        i = name_to_idx[src_name]
        for dst_name, dist in data["distances"].items():
            j = name_to_idx[dst_name]
            distance_matrix[i][j] = dist

    # Menentukan berat paket per index
    package_weights = [graph_data[name]["package_weight"] for name in node_names]

    return node_names, distance_matrix, package_weights, config


# ======================================================================
# UJI COBA FILE data.json
# ======================================================================
if __name__ == "__main__":
    import os

    # Lokasi data.json
    BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    JSON_PATH = os.path.join(BASE_DIR, "data", "data.json")

    # Memuat data dari file
    node_names, distance_matrix, package_weights, config = load_graph_from_json(JSON_PATH)

    fuel_full  = config["fuel_consumption"]["full_load_per_km"]
    fuel_empty = config["fuel_consumption"]["empty_load_per_km"]

    print("="*50)
    print("ALGORITMA GREEDY (NEAREST NEIGHBOR HEURISTIC)")
    print("="*50)
    print(f"Jumlah Lokasi : {len(node_names)} node ({len(node_names)-1} pelanggan + 1 Hub)")
    print(f"Hub           : {node_names[0]}")
    print()

    # Menjalankan algoritma greedy
    finder = GreedyRouteFinder(
        distance_matrix = distance_matrix,
        package_weights = package_weights,
        fuel_full = fuel_full,
        fuel_empty = fuel_empty,
    )
    hasil = finder.solve()

    # Menampilkan rute terpilih dengan nama lokasi
    named_route = " \n    ".join(node_names[i] for i in hasil["path"])
    print(f"Rute Terpilih  :\n    {named_route}")
    print()
    print(f"Jarak Tempuh   : {hasil['distance_km']:.4f} km")
    print(f"Total Bensin   : {hasil['total_fuel_liters']:.4f} liter")
    print(f"Waktu Eksekusi : {hasil['execution_time_ms']:.6f} ms")
    print()

    # Menampilkan detail konsumsi bensin per segmen
    print("-"*50)
    print("Detail Konsumsi Bensin per Segmen:")
    print("-"*50)
    for i, fuel in enumerate(hasil["segment_fuel"]):
        src_name = node_names[hasil["path"][i]]
        dst_name = node_names[hasil["path"][i + 1]]
        dist_seg = distance_matrix[hasil["path"][i]][hasil["path"][i + 1]]
        print(f"[{i+1:>2}] {src_name} -> {dst_name}")
        print(f"Jarak: {dist_seg:.3f} km | Bensin: {fuel:.4f} liter")
        print()
    print("-"*60)
    print(f"TOTAL : {hasil['distance_km']:.4f} km | {hasil['total_fuel_liters']:.4f} liter")