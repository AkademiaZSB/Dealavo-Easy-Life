import os
import re
import json
from PIL import Image, ImageDraw, ImageFont

OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "output")

KOL_TLO_NAGLOWEK = (52, 73, 94)
KOL_TEKST_NAGLOWEK = (255, 255, 255)
KOL_TLO_WIERSZ = (255, 255, 255)
KOL_TLO_ZAZNACZONY = (255, 235, 100)
KOL_TLO_WIERSZ_PARZYSTY = (245, 245, 245)
KOL_TEKST = (30, 30, 30)
KOL_RAMKA = (180, 180, 180)

def czy_podswietlona(kol, war, retailers):
    if not kol or not war:
        return False
    kol_lower = kol.strip().lower()
    if kol_lower == "retailer name":
        return any(r.lower() in war.lower() for r in retailers)
    if kol_lower == "price":
        return True
    return False

def generuj_png(sciezka_png, fraza, wyniki, retailers):
    if not wyniki:
        print("Brak wierszy do wyświetlenia — plik PNG nie zostanie wygenerowany.")
        return

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
    szerokosc = sum(szerkosci) + 1
    wysokosc = margines_gory + wysokosc_wiersza + (wysokosc_wiersza * len(wyniki)) + wysokosc_podpisu + 10

    img = Image.new("RGB", (szerokosc, wysokosc), (245, 245, 245))
    draw = ImageDraw.Draw(img)

    x = 0
    for i, kol in enumerate(kolumny):
        draw.rectangle([x, margines_gory, x + szerkosci[i], margines_gory + wysokosc_wiersza], fill=KOL_TLO_NAGLOWEK, outline=KOL_RAMKA)
        draw.text((x + padding, margines_gory + 8), str(kol), font=font, fill=KOL_TEKST_NAGLOWEK)
        x += szerkosci[i]

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

    y_podpis = wysokosc - wysokosc_podpisu
    pliki_info = ", ".join(set(w["plik"] for w in wyniki))
    draw.text((10, y_podpis), f"Fraza: {fraza}  |  Pliki: {pliki_info}", font=font, fill=(120, 120, 120))

    img.save(sciezka_png)
    print(f"  Zrzut zaktualizowany: {sciezka_png}")

def main():
    print("=== Edytor zrzutów CHECKQLUID ===\n")

    pliki_json = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]
    if not pliki_json:
        print("Brak plików do edycji w folderze output/.")
        return

    print("Dostępne zrzuty:")
    for i, f in enumerate(pliki_json, 1):
        print(f"  {i}. {f.replace('.json', '')}")

    wybor = input("\nKtóre zrzuty edytować? (wpisz numery oddzielone spacją lub przecinkiem, np. 1 3 5): ").strip()
    try:
        numery = [int(x) - 1 for x in re.split(r'[,\s]+', wybor) if x.strip()]
        wybrane_pliki = [pliki_json[i] for i in numery]
    except (ValueError, IndexError):
        print("Nieprawidłowy wybór.")
        return

    print("\nWpisz wartości Source do usunięcia ze wszystkich wybranych zrzutów (jeden per linia, pusta linia kończy):")
    do_usuniecia = []
    while True:
        s = input().strip()
        if s == "":
            break
        do_usuniecia.append(s.lower())

    if not do_usuniecia:
        print("Nie podano żadnych wartości — brak zmian.")
        return

    for plik_json in wybrane_pliki:
        sciezka_json = os.path.join(OUTPUT_FOLDER, plik_json)
        with open(sciezka_json, "r", encoding="utf-8") as f:
            dane = json.load(f)

        fraza = dane["fraza"]
        retailers = dane["retailers"]
        wyniki = dane["wyniki"]

        wyniki_po = [
            w for w in wyniki
            if not any(
                kol.strip().lower() == "source" and (war or "").lower() in do_usuniecia
                for kol, war in w["dane"].items()
            )
        ]

        usunieto = len(wyniki) - len(wyniki_po)
        print(f"\n[{fraza}] Usunięto {usunieto} wiersz(y). Pozostało: {len(wyniki_po)}.")

        dane["wyniki"] = wyniki_po
        with open(sciezka_json, "w", encoding="utf-8") as f:
            json.dump(dane, f, ensure_ascii=False, indent=2)

        sciezka_png = sciezka_json.replace(".json", ".png")
        generuj_png(sciezka_png, fraza, wyniki_po, retailers)

if __name__ == "__main__":
    main()
