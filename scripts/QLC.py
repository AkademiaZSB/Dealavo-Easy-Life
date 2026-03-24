import os
import re
import json

OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "output")

def main():
    print("=== QLC — Czyszczenie historii ===\n")

    pliki_json = sorted([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")])
    pliki_png = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".png")]

    if not pliki_json:
        print("Brak plików do usunięcia.")
        return

    print("Zapisane wyniki:")
    for i, f in enumerate(pliki_json, 1):
        print(f"  {i}. {f.replace('.json', '')}")

    print("\nWpisz numery do usunięcia (np. 1 3 5), lub 'all' aby usunąć wszystkie:")
    wybor = input("> ").strip().lower()

    if not wybor:
        print("Anulowano.")
        return

    if wybor == "all":
        wybrane = pliki_json[:]
    else:
        try:
            numery = [int(x) - 1 for x in re.split(r'[,\s]+', wybor) if x.strip()]
            wybrane = [pliki_json[i] for i in numery]
        except (ValueError, IndexError):
            print("Nieprawidłowy wybór.")
            return

    print(f"\nDo usunięcia ({len(wybrane)}):")
    for f in wybrane:
        print(f"  - {f.replace('.json', '')}")

    potwierdzenie = input("\nCzy na pewno? (tak/nie): ").strip().lower()
    if potwierdzenie != "tak":
        print("Anulowano.")
        return

    usunieto = 0
    for plik_json in wybrane:
        # Usuń JSON
        sciezka_json = os.path.join(OUTPUT_FOLDER, plik_json)
        if os.path.exists(sciezka_json):
            os.remove(sciezka_json)
            usunieto += 1

        # Usuń powiązany PNG
        plik_png = plik_json.replace(".json", ".png")
        sciezka_png = os.path.join(OUTPUT_FOLDER, plik_png)
        if os.path.exists(sciezka_png):
            os.remove(sciezka_png)

    print(f"\n✓ Usunięto {usunieto} wynik(ów).")

if __name__ == "__main__":
    main()
