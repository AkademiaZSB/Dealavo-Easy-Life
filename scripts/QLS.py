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

def sprawdz_captche(page, retailer):
    """Sprawdza czy strona ma captchę. Zwraca (jest_captcha, jest_retailer)."""
    page.wait_for_timeout(3000)
    tresc = page.content().lower()
    jest_captcha = any(x in tresc for x in ["captcha", "robot", "verify you are human", "challenge"])
    jest_retailer = retailer.lower() in tresc
    return jest_captcha, jest_retailer

def czekaj_na_zaladowanie(page, retailer):
    """Czeka na załadowanie strony (bez captchy). Zwraca True jeśli retailer widoczny."""
    for proba in range(15):  # max 30 sekund
        page.wait_for_timeout(2000)
        tresc = page.content().lower()
        jest_captcha = any(x in tresc for x in ["captcha", "robot", "verify you are human", "challenge"])
        jest_retailer = retailer.lower() in tresc

        if jest_retailer:
            return True
        if jest_captcha:
            return False
        if proba > 4:
            return False
    return False

def zrob_screenshot(page, url, retailer, fraza, idx, folder):
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        czekaj_na_zaladowanie(page, retailer)

        retailer_lower = retailer.lower()
        candidates = page.locator(f"text={retailer}").all()
        if not candidates:
            candidates = page.locator(
                f"xpath=//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{retailer_lower}')]"
            ).all()

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
        print(f"  ✗ Błąd: {e}")
        return False

def zbierz_zadania(pliki):
    """Wczytuje wszystkie zadania z plików JSON."""
    zadania = []
    for plik_json in pliki:
        sciezka_json = os.path.join(OUTPUT_FOLDER, plik_json)
        with open(sciezka_json, "r", encoding="utf-8") as f:
            dane = json.load(f)

        fraza = dane["fraza"]
        wyniki = dane["wyniki"]

        for idx, wynik in enumerate(wyniki, 1):
            url = None
            retailer_name = None
            for kol, war in wynik["dane"].items():
                if kol and "product url" in kol.lower() and war:
                    url = war
                if kol and "retailer name" in kol.lower() and war:
                    retailer_name = war

            if url and retailer_name:
                zadania.append({"fraza": fraza, "url": url, "retailer": retailer_name, "idx": idx})

    return zadania

def main():
    print("=== QLS — Screenshoty z Product URL ===\n")

    pliki = wybierz_pliki_json()
    if not pliki:
        return

    zadania = zbierz_zadania(pliki)
    if not zadania:
        print("Brak wyników z Product URL.")
        return

    screenshots_folder = os.path.join(OUTPUT_FOLDER, "screenshots")
    os.makedirs(screenshots_folder, exist_ok=True)

    # --- FAZA 1: Headless — sprawdź captchy i rób screenshoty ---
    print(f"\nPrzetwarzam {len(zadania)} wynik(ów) w tle...\n")

    z_captcha = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        for zadanie in zadania:
            print(f"  [{zadanie['fraza']}] Retailer: {zadanie['retailer']}")
            try:
                page.goto(zadanie["url"], timeout=30000, wait_until="domcontentloaded")
                jest_captcha, jest_retailer = sprawdz_captche(page, zadanie["retailer"])

                if jest_captcha and not jest_retailer:
                    print(f"  ⚠ Captcha wykryta — odkładam na później.")
                    z_captcha.append(zadanie)
                else:
                    zrob_screenshot(page, zadanie["url"], zadanie["retailer"],
                                    zadanie["fraza"], zadanie["idx"], screenshots_folder)
            except Exception as e:
                print(f"  ✗ Błąd: {e}")

        browser.close()

    # --- FAZA 2: Captcha — zapytaj użytkownika ---
    if z_captcha:
        print(f"\n⚠  Wykryto captchę na {len(z_captcha)} wyniku/wynikach.")
        for z in z_captcha:
            print(f"   - [{z['fraza']}] {z['retailer']}")
        odpowiedz = input("\nCzy chcesz otworzyć te strony i rozwiązać captchę ręcznie? (tak/nie): ").strip().lower()

        if odpowiedz == "tak":
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page(viewport={"width": 1400, "height": 900})

                for zadanie in z_captcha:
                    print(f"\n  [{zadanie['fraza']}] Retailer: {zadanie['retailer']}")
                    print(f"  Otwieram stronę — rozwiąż captchę, czekam...")
                    try:
                        page.goto(zadanie["url"], timeout=30000, wait_until="domcontentloaded")
                        page.wait_for_timeout(3000)

                        # Czekaj tylko jeśli captcha nadal aktywna (max 120 sekund)
                        for _ in range(60):
                            tresc = page.content().lower()
                            jest_captcha = any(x in tresc for x in ["captcha", "robot", "verify you are human", "challenge"])
                            if not jest_captcha:
                                break
                            page.wait_for_timeout(2000)

                        print(f"  Strona gotowa — robię screenshot...")
                        zrob_screenshot(page, zadanie["url"], zadanie["retailer"],
                                        zadanie["fraza"], zadanie["idx"], screenshots_folder)
                    except Exception as e:
                        print(f"  ✗ Błąd: {e}")

                browser.close()
        else:
            print("Pominięto strony z captchą.")

    print(f"\n=== Gotowe! Screenshoty w: output/screenshots/ ===")

if __name__ == "__main__":
    main()
