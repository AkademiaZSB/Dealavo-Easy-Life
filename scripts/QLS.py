import os
import re
import json
from playwright.sync_api import sync_playwright

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

def czekaj_na_zaladowanie(page, retailer):
    """Czeka aż strona się załaduje i nie ma captchy."""
    retailer_lower = retailer.lower()
    print(f"  Czekam na załadowanie strony...")

    for proba in range(30):  # max 60 sekund
        page.wait_for_timeout(2000)

        # Sprawdź czy captcha jest aktywna
        tresc = page.content().lower()
        jest_captcha = any(x in tresc for x in ["captcha", "robot", "verify you are human", "challenge"])
        jest_retailer = retailer_lower in tresc

        if jest_captcha and not jest_retailer:
            if proba == 0:
                print(f"  ⚠️  Wykryto captchę — rozwiąż ją w oknie przeglądarki, czekam...")
            continue

        if jest_retailer:
            print(f"  Strona załadowana.")
            return True

        if proba > 5 and not jest_retailer:
            print(f"  Strona załadowana, ale retailer niewidoczny.")
            return False

    print(f"  ✗ Timeout — strona nie załadowała się w 60 sekund.")
    return False

def zrob_screenshot(page, url, retailer, fraza, idx, folder):
    try:
        print(f"  Otwieram: {url}")
        page.goto(url, timeout=30000, wait_until="domcontentloaded")

        zaladowana = czekaj_na_zaladowanie(page, retailer)

        retailer_lower = retailer.lower()

        # Szukaj elementu zawierającego nazwę retailera
        candidates = page.locator(f"text={retailer}").all()
        if not candidates:
            candidates = page.locator(f"xpath=//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{retailer_lower}')]").all()

        bezpieczna_fraza = re.sub(r'[^\w\-]', '_', fraza)
        bezpieczny_retailer = re.sub(r'[^\w\-]', '_', retailer)

        if candidates:
            element = candidates[0]
            try:
                rodzic_tr = element.locator("xpath=ancestor::tr[1]")
                if rodzic_tr.count() > 0:
                    element = rodzic_tr
                else:
                    element = candidates[0].locator("xpath=ancestor::*[3]")
            except:
                element = candidates[0]

            nazwa_pliku = f"{bezpieczna_fraza}_{bezpieczny_retailer}_{idx}.png"
            sciezka = os.path.join(folder, nazwa_pliku)
            element.first.screenshot(path=sciezka)
            print(f"  ✓ Screenshot zapisany: {nazwa_pliku}")
            return True
        else:
            print(f"  ✗ Nie znaleziono '{retailer}' na stronie — zapisuję całą stronę.")
            nazwa_pliku = f"{bezpieczna_fraza}_{bezpieczny_retailer}_{idx}_calastrona.png"
            sciezka = os.path.join(folder, nazwa_pliku)
            page.screenshot(path=sciezka, full_page=False)
            print(f"  → Zapisano: {nazwa_pliku}")
            return False

    except Exception as e:
        print(f"  ✗ Błąd dla {url}: {e}")
        return False

def main():
    print("=== QLS — Screenshoty z Product URL ===\n")

    pliki = wybierz_pliki_json()
    if not pliki:
        return

    screenshots_folder = os.path.join(OUTPUT_FOLDER, "screenshots")
    os.makedirs(screenshots_folder, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        for plik_json in pliki:
            sciezka_json = os.path.join(OUTPUT_FOLDER, plik_json)
            with open(sciezka_json, "r", encoding="utf-8") as f:
                dane = json.load(f)

            fraza = dane["fraza"]
            retailers = dane["retailers"]
            wyniki = dane["wyniki"]

            print(f"\n=== Fraza: {fraza} ===")

            for idx, wynik in enumerate(wyniki, 1):
                url = None
                retailer_name = None

                for kol, war in wynik["dane"].items():
                    if kol and "product url" in kol.lower() and war:
                        url = war
                    if kol and "retailer name" in kol.lower() and war:
                        retailer_name = war

                if not url:
                    print(f"  Wiersz {idx}: brak Product URL — pomijam.")
                    continue
                if not retailer_name:
                    print(f"  Wiersz {idx}: brak Retailer Name — pomijam.")
                    continue

                print(f"\n  Wiersz {idx} | Retailer: {retailer_name}")
                zrob_screenshot(page, url, retailer_name, fraza, idx, screenshots_folder)

        browser.close()

    print(f"\n=== Gotowe! Screenshoty w: output/screenshots/ ===")

if __name__ == "__main__":
    main()
