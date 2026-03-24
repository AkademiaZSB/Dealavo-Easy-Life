import os
import re
import json
import webbrowser

OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "output")

def wybierz_pliki_json():
    pliki_json = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]
    if not pliki_json:
        print("Brak plików JSON w folderze output/.")
        return []

    print("Dostępne wyniki:")
    for i, f in enumerate(pliki_json, 1):
        print(f"  {i}. {f.replace('.json', '')}")

    wybor = input("\nKtóre wyniki? (numery oddzielone spacją, lub Enter = wszystkie): ").strip()
    if not wybor:
        return pliki_json

    try:
        numery = [int(x) - 1 for x in re.split(r'[,\s]+', wybor) if x.strip()]
        return [pliki_json[i] for i in numery]
    except (ValueError, IndexError):
        print("Nieprawidłowy wybór.")
        return []

def main():
    print("=== QLS — Linki z Product URL ===\n")

    pliki = wybierz_pliki_json()
    if not pliki:
        return

    linki = []

    for plik_json in pliki:
        sciezka_json = os.path.join(OUTPUT_FOLDER, plik_json)
        with open(sciezka_json, "r", encoding="utf-8") as f:
            dane = json.load(f)

        fraza = dane["fraza"]
        wyniki = dane["wyniki"]

        print(f"\n=== Fraza: {fraza} ===")

        for wynik in wyniki:
            url = None
            retailer_name = None
            for kol, war in wynik["dane"].items():
                if kol and "product url" in kol.lower() and war:
                    url = war
                if kol and "retailer name" in kol.lower() and war:
                    retailer_name = war

            if url:
                print(f"  [{retailer_name or '?'}] {url}")
                linki.append(url)
            else:
                print(f"  [{retailer_name or '?'}] brak Product URL")

    if not linki:
        print("\nBrak linków do otwarcia.")
        return

    print(f"\nZnaleziono {len(linki)} link(ów).")
    odpowiedz = input("Czy chcesz otworzyć je w przeglądarce? (tak/nie): ").strip().lower()

    if odpowiedz == "tak":
        for url in linki:
            webbrowser.open(url)
        print("Linki otwarte.")
    else:
        print("Linki nie zostały otwarte.")

if __name__ == "__main__":
    main()
