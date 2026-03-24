import os
import shutil

FOLDER = os.path.expanduser("~/Downloads/QL")

def main():
    print("=== QLCC — Czyszczenie folderu ~/Downloads/QL ===\n")

    if not os.path.exists(FOLDER):
        print(f"Folder '{FOLDER}' nie istnieje.")
        return

    pliki = os.listdir(FOLDER)
    if not pliki:
        print("Folder jest już pusty.")
        return

    print(f"Znaleziono {len(pliki)} plik(ów) w {FOLDER}:")
    for f in pliki:
        print(f"  - {f}")

    odpowiedz = input("\nCzy na pewno chcesz usunąć wszystkie pliki? (tak/nie): ").strip().lower()
    if odpowiedz != "tak":
        print("Anulowano.")
        return

    for f in pliki:
        sciezka = os.path.join(FOLDER, f)
        try:
            if os.path.isfile(sciezka):
                os.remove(sciezka)
            elif os.path.isdir(sciezka):
                shutil.rmtree(sciezka)
        except Exception as e:
            print(f"  ✗ Nie udało się usunąć '{f}': {e}")

    print(f"\n✓ Folder wyczyszczony.")

if __name__ == "__main__":
    main()
