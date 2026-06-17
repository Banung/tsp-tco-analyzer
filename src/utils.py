import json
import os


class FuelCalculator:
    """Modul tersentralisasi untuk menghitung logika bensin logistik."""

    def __init__(self, max_capacity, fuel_full, fuel_empty):
        self.max_capacity = max_capacity
        self.fuel_full = fuel_full
        self.fuel_empty = fuel_empty

    def get_fuel_ratio(self, current_load):
        """Menghitung rasio liter/km berdasarkan persentase beban motor."""
        # Mencegah nilai rasio lebih dari 1.0 jika beban melebihi kapasitas
        load_ratio = min(current_load / self.max_capacity, 1.0)
        return self.fuel_empty + load_ratio * (self.fuel_full - self.fuel_empty)

    def calculate_route_fuel(self, path, distance_matrix, package_weights):
        """
        Mensimulasikan perjalanan untuk menghitung bensin yang dihabiskan
        berdasarkan pengurangan beban di setiap titik.
        """
        segment_fuel = []
        total_fuel = 0.0
        current_load = sum(package_weights)  # Bawa semua paket dari Hub

        for i in range(len(path) - 1):
            src = path[i]
            dst = path[i + 1]
            dist = distance_matrix[src][dst]

            # Hitung bensin yang dipakai di segmen jalan ini
            ratio = self.get_fuel_ratio(current_load)
            used = dist * ratio
            segment_fuel.append(used)
            total_fuel += used

            # Sampai di titik tujuan, turunkan paket
            current_load -= package_weights[dst]
            current_load = max(0.0, current_load)  # Jaga-jaga agar tidak negatif

        return total_fuel, segment_fuel


def load_graph_from_json(json_path):
    """Fungsi Parser JSON ke Matriks Ketetanggaan."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File tidak ditemukan: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    config = raw["config"]
    graph_data = raw["graph_data"]

    # Menyusun urutan: Hub di index 0
    all_names = list(graph_data.keys())
    hub_name = all_names[0]
    node_names = [hub_name] + [n for n in all_names if n != hub_name]
    n = len(node_names)

    name_to_idx = {name: i for i, name in enumerate(node_names)}

    # Membangun Adjacency Matrix
    distance_matrix = [[0.0] * n for _ in range(n)]
    for src_name, data in graph_data.items():
        if src_name not in name_to_idx:
            continue
        i = name_to_idx[src_name]
        for dst_name, dist in data["distances"].items():
            if dst_name in name_to_idx:
                j = name_to_idx[dst_name]
                distance_matrix[i][j] = dist

    package_weights = [graph_data[name]["package_weight"] for name in node_names]

    return node_names, distance_matrix, package_weights, config
