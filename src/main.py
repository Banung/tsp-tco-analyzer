import argparse
import os
import sys

from algo_exact import ExactRouteFinder
from greedy import GreedyRouteFinder
from utils import FuelCalculator, load_graph_from_json


def print_separator(title=""):
    """Helper untuk mempercantik output terminal"""
    print(f"\n{'-' * 60}")
    if title:
        print(f"{title.center(60)}")
        print(f"{'-' * 60}")


def main():
    # 1. SETUP COMMAND LINE INTERFACE (CLI)
    parser = argparse.ArgumentParser(
        description="Simulasi TCO Last-Mile Delivery (Exact vs Heuristic)"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        required=True,
        help="Pilih skenario ekonomi (contoh: subsidi, krisis)",
    )
    args = parser.parse_args()
    selected_scenario = args.scenario.lower()

    # 2. LOAD DATA DARI JSON
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "data", "data.json")

    try:
        node_names, distance_matrix, package_weights, config = load_graph_from_json(
            json_path
        )
    except Exception as e:
        print(f"Error membaca JSON: {e}")
        sys.exit(1)

    # 3. VALIDASI SKENARIO BISNIS
    if selected_scenario not in config["scenarios"]:
        print(f"Error: Skenario '{selected_scenario}' tidak ditemukan di data.json!")
        print(f"Skenario yang tersedia: {list(config['scenarios'].keys())}")
        sys.exit(1)

    # Ambil variabel finansial dari JSON
    fuel_price = config["scenarios"][selected_scenario]["fuel_price_per_liter"]
    server_cost_per_ms = config["server_cost_per_ms"]

    fuel_config = config["fuel_consumption"]

    print_separator("SIMULASI LAST-MILE DELIVERY")
    print(f"Skenario     : {selected_scenario.upper()}")
    print(f"Harga BBM    : Rp {fuel_price:,.0f} / liter")
    print(f"Harga Server : Rp {server_cost_per_ms:,.0f} / ms")
    print(f"Jumlah Node  : {len(node_names)} titik")

    # 4. INISIALISASI UTILITY DAN SOLVER
    fuel_calc = FuelCalculator(
        max_capacity=fuel_config["max_vehicle_capacity_kg"],
        fuel_full=fuel_config["full_load_per_km"],
        fuel_empty=fuel_config["empty_load_per_km"],
    )

    greedy_solver = GreedyRouteFinder(distance_matrix, package_weights, fuel_calc)
    exact_solver = ExactRouteFinder(distance_matrix, package_weights, fuel_calc)

    # 5. EKSEKUSI ALGORITMA
    print("\nMenjalankan Algoritma A (Heuristik / Greedy)...")
    greedy_result = greedy_solver.solve()

    print("Menjalankan Algoritma B (Eksak / DFS)...")
    exact_result = exact_solver.solve()

    # 6. HITUNG TCO (Total Cost of Ownership)
    def calculate_tco(result):
        biaya_bensin = result["total_fuel_liters"] * fuel_price
        biaya_server = result["execution_time_ms"] * server_cost_per_ms
        tco_total = biaya_bensin + biaya_server
        return biaya_bensin, biaya_server, tco_total

    greedy_bensin, greedy_server, greedy_tco = calculate_tco(greedy_result)
    exact_bensin, exact_server, exact_tco = calculate_tco(exact_result)

    # 7. LAPORAN BISNIS FINAL
    print_separator("HASIL KOMPARASI TOTAL COST OF OWNERSHIP (TCO)")

    # Fungsi helper untuk print metrik
    def print_metrics(name, result, bensin, server, tco):
        print(f"[{name}]")
        print(f"  Jarak Tempuh  : {result['distance_km']:.2f} km")
        print(f"  Total Bensin  : {result['total_fuel_liters']:.3f} L")
        print(f"  Waktu Server  : {result['execution_time_ms']:.4f} ms")
        print("  Rincian Biaya:")
        print(f"    - Bensin    : Rp {bensin:,.2f}")
        print(f"    - Server    : Rp {server:,.2f}")
        print(f"  TOTAL TCO     : Rp {tco:,.2f}\n")

    print_metrics(
        "ALGORITMA A (GREEDY)", greedy_result, greedy_bensin, greedy_server, greedy_tco
    )
    print_metrics(
        "ALGORITMA B (EKSAK / DFS)", exact_result, exact_bensin, exact_server, exact_tco
    )

    # Kesimpulan Pemenang
    print_separator("KESIMPULAN BISNIS")
    if greedy_tco < exact_tco:
        diff = exact_tco - greedy_tco
        print(f"Rekomendasi: ALGORITMA GREEDY.")
        print(f"Meskipun rute Eksak lebih pendek, biaya servernya membuat ")
        print(f"perusahaan rugi Rp {diff:,.2f} dibanding pakai Greedy.")
    else:
        diff = greedy_tco - exact_tco
        print(f"Rekomendasi: ALGORITMA EKSAK.")
        print(f"Penghematan bensin dari rute optimal berhasil menutupi")
        print(f"biaya server. Perusahaan untung Rp {diff:,.2f} dibanding pakai Greedy.")
    print_separator()


if __name__ == "__main__":
    main()
