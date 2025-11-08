import time
import os
import duckdb
from auto_simulator import AutoSimulator
from drive_simulator import DriveSimulator, get_route_coordinates, get_route_coords, load_serbian_roads, show_route_distances

YEAR = 2024
DATASET_FOLDER = "./dataset"
TABLE_NAME = "accidents"

# ------------------------------
# Učitati podatke o nezgodama
# ------------------------------
def load_accidents_data():
    con = duckdb.connect()
    # Učitaj spatial extension
    con.execute("INSTALL spatial;")
    con.execute("LOAD spatial;")

    print("=" * 70)
    print("UČITAVANJE PODATAKA")
    print("=" * 70)
    # kreiramo duckdb tabelu pomocu excel fajla
    file_name = os.path.join(DATASET_FOLDER, f"nez-opendata-{YEAR}-{YEAR+1}0125.xlsx")
    create_table_query = f"""
    CREATE TABLE {TABLE_NAME} AS
    SELECT  
        A1::BIGINT        AS accident_id,             
        strptime(D1, '%d.%m.%Y,%H:%M') AS event_time,
        F1::DOUBLE        AS lat,
        E1::DOUBLE        AS lon,
        I1                AS description
     FROM read_xlsx('{file_name}');
    """
    con.execute(create_table_query)
    count = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
    print(f"Ucitano {count} mesta nezgoda, iz {YEAR} godine")
    print("Kreiranje hilbert indexa...")
    con.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN hilbert_value UINTEGER;")
    con.execute(f"UPDATE {TABLE_NAME} SET hilbert_value = ST_Hilbert(ST_Point(lon, lat));")
    con.execute(f"CREATE INDEX {TABLE_NAME}_hilbert_idx ON {TABLE_NAME}(hilbert_value);")
    print("Indeks kreiran")
    cols = con.execute(f"Describe {TABLE_NAME}").fetchall()
    print("Kolone:")
    for col in cols:
        print(col[0],col[1])


# OVDE UNETI KOD KOJI ĆE PROVERAVATI OKOLINU AUTOMOBILA
def check_accident_zone(lat, lon):
    a = 1


if __name__ == "__main__":

    # ------------------------------
    # Učitaj podatke o nezgodama
    # ------------------------------
    load_accidents_data()
    # -------------------------------
    # -------------------------------



    # start_city = "Prijepolje"
    # end_city = "Užice"

    # # 1. Učitaj mrežu puteva Srbije
    # G = load_serbian_roads()
    
    # print(f"Ucitana mreža puteva Srbije! {len(G.nodes)} čvorova, {len(G.edges)} ivica.")

    # # 2. Odredjivanje koordinata pocetka i kraja rute
    # orig, dest = get_route_coordinates(start_city, end_city)

    # # 3. Odredjivanje rute
    # route_coords, route = get_route_coords(G, orig, dest)
    
    # #show_route_distances(route_coords)
    
    # # 4. Inicijalizacija grafičke mape za voznju rutom
    # drive_simulator = DriveSimulator(G, edge_color='lightgray', edge_linewidth=0.5)

    # # 5. Prikaz mape sa rutom
    # drive_simulator.prikazi_mapu(route_coords, route_color='blue', auto_marker_color='ro', auto_marker_size=8)
      
    # # 6. Inicijalizuj simulator kretanja automobila sa brzinom 250 km/h i intervalom od 1 sekunde  
    # automobil = AutoSimulator(route_coords, speed_kmh=250, interval=1.0)
    # automobil.running = True

    # print("\n=== Simulacija pokrenuta ===")
    # print("Kontrole: Auto se pomera automatski svakih", automobil.interval, "sekundi")
    # print("Za zaustavljanje pritisnite Ctrl+C\n")
    
    # interval_simulacije = 1.0  # sekunde
    # # 7. Glavna petlja simulacije
    # try:
    #     step_count = 0
    #     while automobil.running:
    #         # Pomeri automobil
    #         auto_current_pos = automobil.move()
    #         lat, lon = auto_current_pos
            
    #         drive_simulator.move_auto_marker(lat, lon, automobil.get_progress_info(), plot_pause=0.01)
                        
            
    #         # Pozovi check_neighbourhood samo na svakih 5 koraka (da ne zatrpava konzolu)
    #         step_count += 1
    #         if step_count % 5 == 0:
    #             # -------------------------------
    #             # -------------------------------
    #             check_accident_zone(lat, lon)
    #             # -------------------------------
    #             # -------------------------------
            
    #         # Proveri da li je stigao na kraj
    #         if automobil.is_finished():
    #             print("\n=== Automobil je stigao na destinaciju! ===")
    #             break
            
    #         # Čekaj interval pre sledećeg pomeraja
    #         time.sleep(interval_simulacije)
            
    # except KeyboardInterrupt:
    #     print("\n\n=== Simulacija prekinuta ===")
    
    
    # drive_simulator.finish_drive()
    


    
