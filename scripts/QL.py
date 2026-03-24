import os
import csv
import re
import json
from PIL import Image, ImageDraw, ImageFont

FOLDER = os.path.expanduser("~/Downloads/QL")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "output")

# Kolory
KOL_TLO_NAGLOWEK = (52, 73, 94)
KOL_TEKST_NAGLOWEK = (255, 255, 255)
KOL_TLO_WIERSZ = (255, 255, 255)
KOL_TLO_ZAZNACZONY = (255, 235, 100)
KOL_TLO_WIERSZ_PARZYSTY = (245, 245, 245)
KOL_TEKST = (30, 30, 30)
KOL_RAMKA = (180, 180, 180)

def wykryj_separator(sciezka):
    with open(sciezka, "r", encoding="utf-8", errors="ignore") as f:
        probka = f.read(4096)
    if probka.count("\t") >= probka.count(","):
        return "\t"
    return ","

def czy_podswietlona(kol, war, retailers):
    if not kol or not war:
        return False
    kol_lower = kol.strip().lower()
    if kol_lower == "retailer name":
        return any(r.lower() in war.lower() for r in retailers)
    if kol_lower == "price":
        return True
    return False

def zapisz_obraz(fraza, wyniki, retailers):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    bezpieczna_nazwa = re.sub(r'[^\w\-]', '_', fraza)
    sciezka_png = os.path.join(OUTPUT_FOLDER, f"{bezpieczna_nazwa}.png")

    if not wyniki:
        return None

    kolumny = list(wyniki[0]["dane"].keys())

    font = None
    kandidaci = [
        "/System/Library/Fonts/Helvetica.ttc",           # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", # Linux
        "C:/Windows/Fonts/arial.ttf",                     # Windows
    ]
    for sciezka_fontu in kandidaci:
        try:
            font = ImageFont.truetype(sciezka_fontu, 14)
            break
        except:
            continue
    if font is None:
        font = ImageFont.load_default()

    padding = 10
    min_szer = 80

    # Oblicz szerokości kolumn na podstawie wszystkich wierszy
    szerkosci = []
    for kol in kolumny:
        w_max = font.getlength(str(kol)) + padding * 2
        for wynik in wyniki:
            war = wynik["dane"].get(kol, "") or ""
            w = font.getlength(str(war)) + padding * 2
            if w > w_max:
                w_max = w
        szerkosci.append(max(min_szer, int(w_max)))

    wysokosc_wiersza = 30
    margines_gory = 10
    wysokosc_podpisu = 20
    liczba_wierszy = len(wyniki)
    szerokosc = sum(szerkosci) + 1
    wysokosc = margines_gory + wysokosc_wiersza + (wysokosc_wiersza * liczba_wierszy) + wysokosc_podpisu + 10

    img = Image.new("RGB", (szerokosc, wysokosc), (245, 245, 245))
    draw = ImageDraw.Draw(img)

    # Nagłówek
    x = 0
    for i, kol in enumerate(kolumny):
        draw.rectangle([x, margines_gory, x + szerkosci[i], margines_gory + wysokosc_wiersza], fill=KOL_TLO_NAGLOWEK, outline=KOL_RAMKA)
        draw.text((x + padding, margines_gory + 8), str(kol), font=font, fill=KOL_TEKST_NAGLOWEK)
        x += szerkosci[i]

    # Wiersze danych
    for idx, wynik in enumerate(wyniki):
        y = margines_gory + wysokosc_wiersza + idx * wysokosc_wiersza
        tlo_domyslne = KOL_TLO_WIERSZ if idx % 2 == 0 else KOL_TLO_WIERSZ_PARZYSTY
        x = 0
        for i, kol in enumerate(kolumny):
            war = wynik["dane"].get(kol, "") or ""
            tlo = KOL_TLO_ZAZNACZONY if czy_podswietlona(kol, war, retailers) else tlo_domyslne
            draw.rectangle([x, y, x + szerkosci[i], y + wysokosc_wiersza], fill=tlo, outline=KOL_RAMKA)
            draw.text((x + padding, y + 8), str(war), font=font, fill=KOL_TEKST)
            x += szerkosci[i]

    # Podpis
    y_podpis = wysokosc - wysokosc_podpisu
    pliki_info = ", ".join(set(w["plik"] for w in wyniki))
    draw.text((10, y_podpis), f"Fraza: {fraza}  |  Pliki: {pliki_info}", font=font, fill=(120, 120, 120))

    img.save(sciezka_png)

    # Zapisz dane do JSON (potrzebne do edycji zrzutu)
    sciezka_json = sciezka_png.replace(".png", ".json")
    with open(sciezka_json, "w", encoding="utf-8") as f:
        json.dump({"fraza": fraza, "retailers": retailers, "wyniki": wyniki}, f, ensure_ascii=False, indent=2)

    return sciezka_png

def szukaj(fraza, retailers):
    if not os.path.exists(FOLDER):
        print(f"Błąd: folder '{FOLDER}' nie istnieje.")
        return

    pliki = [f for f in os.listdir(FOLDER) if os.path.isfile(os.path.join(FOLDER, f))]

    if not pliki:
        print("Folder jest pusty — brak plików do przeszukania.")
        return

    print(f"\nPrzeszukuję {len(pliki)} plik(ów) w: {FOLDER}\n")

    znalezione = []

    for nazwa_pliku in pliki:
        sciezka = os.path.join(FOLDER, nazwa_pliku)
        try:
            sep = wykryj_separator(sciezka)
            with open(sciezka, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f, delimiter=sep)
                for nr_wiersza, wiersz in enumerate(reader, start=2):
                    wartosci = list(wiersz.values())
                    zawartosc_wiersza = " ".join(v for v in wartosci if v)

                    fraza_ok = fraza.lower() in zawartosc_wiersza.lower()
                    retailer_ok = any(
                        r.lower() in (v or "").lower()
                        for r in retailers
                        for k, v in wiersz.items()
                        if k and "retailer name" in k.lower()
                    )

                    if fraza_ok and retailer_ok:
                        znalezione.append({
                            "plik": nazwa_pliku,
                            "wiersz_nr": nr_wiersza,
                            "dane": wiersz
                        })
        except Exception as e:
            print(f"  Pominięto '{nazwa_pliku}': {e}")

    retailers_znalezione = set()
    if znalezione:
        print(f"✓ ZNALEZIONO — {len(znalezione)} pasujący/ch wiersz(y):\n")
        for wynik in znalezione:
            print(f"  Plik: {wynik['plik']}  |  Wiersz: {wynik['wiersz_nr']}")
            for kolumna, wartosc in wynik['dane'].items():
                if wartosc:
                    print(f"    {kolumna}: {wartosc}")
                    if kolumna and "retailer name" in kolumna.lower():
                        for r in retailers:
                            if r.lower() in wartosc.lower():
                                retailers_znalezione.add(r)
            print()

        sciezka_png = zapisz_obraz(fraza, znalezione, retailers)
        print(f"  Zrzut zapisany: {sciezka_png}\n")
    else:
        print(f"✗ NIE ZNALEZIONO wiersza z frazą \"{fraza}\" i podanymi Retailer Names.\n")

    retailers_nieznalezione = [r for r in retailers if r not in retailers_znalezione]
    if retailers_nieznalezione:
        print(f"--- Nie znaleziono dla UID \"{fraza}\" ---")
        for r in retailers_nieznalezione:
            print(f"  ✗ {r}")

if __name__ == "__main__":
    print("=== Wyszukiwarka fraz ===\n")

    zadania = []
    nr = 1
    while True:
        fraza = input(f"Fraza {nr} (lub Enter aby zakończyć): ").strip()
        if fraza == "":
            break
        print("Wpisz Retailer Names (jeden per linia, pusta linia kończy):")
        retailers = []
        while True:
            r = input().strip()
            if r == "":
                break
            retailers.append(r)
        if retailers:
            frazy = [f.strip() for f in re.split(r'[,\s]+', fraza) if f.strip()]
            for f in frazy:
                zadania.append((f, retailers))
            nr += 1
        else:
            print("Nie podano żadnego Retailer Name — fraza pominięta.\n")

    if not zadania:
        print("Nie podano żadnych fraz.")
    else:
        print(f"\n--- Rozpoczynam wyszukiwanie ({len(zadania)} fraza/frazy) ---\n")
        for fraza, retailers in zadania:
            print(f"=== Fraza: {fraza} ===")
            szukaj(fraza, retailers)
            print()
