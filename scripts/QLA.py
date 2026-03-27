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
KOL_SEPARATOR = (52, 73, 94)

def czy_podswietlona(kol, war, retailers):
    if not kol or not war:
        return False
    kol_lower = kol.strip().lower()
    if kol_lower == "retailer name":
        return any(r.lower() in war.lower() for r in retailers)
    if kol_lower == "price":
        return True
    return False

def wybierz_pliki_json():
    pliki_json = sorted([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")])
    if not pliki_json:
        print("Brak plików JSON w folderze output/.")
        return []

    print("Dostępne wyniki:")
    for i, f in enumerate(pliki_json, 1):
        print(f"  {i}. {f.replace('.json', '')}")

    wybor = input("\nKtóre wyniki połączyć? (numery oddzielone spacją, lub Enter = wszystkie): ").strip()
    if not wybor:
        return pliki_json

    try:
        numery = [int(x) - 1 for x in re.split(r'[,\s]+', wybor) if x.strip()]
        return [pliki_json[i] for i in numery]
    except (ValueError, IndexError):
        print("Nieprawidłowy wybór.")
        return []

def generuj_obraz_polaczony(sekcje, sciezka_png):
    """
    sekcje = lista słowników: {"fraza": str, "wyniki": [...], "retailers": [...]}
    """
    font = None
    for sciezka_fontu in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]:
        try:
            font = ImageFont.truetype(sciezka_fontu, 14)
            break
        except:
            continue
    if font is None:
        font = ImageFont.load_default()

    font_naglowek_sekcji = None
    for sciezka_fontu in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]:
        try:
            font_naglowek_sekcji = ImageFont.truetype(sciezka_fontu, 14)
            break
        except:
            continue
    if font_naglowek_sekcji is None:
        font_naglowek_sekcji = font

    padding = 10
    min_szer = 80
    wysokosc_wiersza = 30
    margines_gory = 10
    wysokosc_naglowka_sekcji = 30

    # Zbierz wszystkie kolumny ze wszystkich sekcji
    wszystkie_kolumny = []
    for sekcja in sekcje:
        if sekcja["wyniki"]:
            for kol in sekcja["wyniki"][0]["dane"].keys():
                if kol not in wszystkie_kolumny:
                    wszystkie_kolumny.append(kol)

    if not wszystkie_kolumny:
        print("Brak danych do połączenia.")
        return

    # Oblicz szerokości kolumn
    szerkosci = []
    for kol in wszystkie_kolumny:
        w_max = font.getlength(str(kol)) + padding * 2
        for sekcja in sekcje:
            for wynik in sekcja["wyniki"]:
                war = wynik["dane"].get(kol, "") or ""
                w = font.getlength(str(war)) + padding * 2
                if w > w_max:
                    w_max = w
        szerkosci.append(max(min_szer, int(w_max)))

    szerokosc = sum(szerkosci) + 1

    # Oblicz wysokość
    wysokosc = margines_gory
    for sekcja in sekcje:
        wysokosc += wysokosc_naglowka_sekcji  # nagłówek sekcji z frazą
        wysokosc += wysokosc_wiersza          # nagłówek kolumn
        wysokosc += wysokosc_wiersza * len(sekcja["wyniki"])
    wysokosc += 10

    img = Image.new("RGB", (szerokosc, wysokosc), (245, 245, 245))
    draw = ImageDraw.Draw(img)

    y = margines_gory

    for sekcja in sekcje:
        fraza = sekcja["fraza"]
        wyniki = sekcja["wyniki"]
        retailers = sekcja["retailers"]

        # Nagłówek sekcji (fraza)
        draw.rectangle([0, y, szerokosc, y + wysokosc_naglowka_sekcji], fill=KOL_SEPARATOR)
        draw.text((padding, y + 8), f"Fraza: {fraza}  ({len(wyniki)} wiersz/y)", font=font_naglowek_sekcji, fill=(255, 255, 255))
        y += wysokosc_naglowka_sekcji

        # Nagłówek kolumn
        x = 0
        for i, kol in enumerate(wszystkie_kolumny):
            draw.rectangle([x, y, x + szerkosci[i], y + wysokosc_wiersza], fill=KOL_TLO_NAGLOWEK, outline=KOL_RAMKA)
            draw.text((x + padding, y + 8), str(kol), font=font, fill=KOL_TEKST_NAGLOWEK)
            x += szerkosci[i]
        y += wysokosc_wiersza

        # Wiersze danych
        for idx, wynik in enumerate(wyniki):
            tlo_domyslne = KOL_TLO_WIERSZ if idx % 2 == 0 else KOL_TLO_WIERSZ_PARZYSTY
            x = 0
            for i, kol in enumerate(wszystkie_kolumny):
                war = wynik["dane"].get(kol, "") or ""
                tlo = KOL_TLO_ZAZNACZONY if czy_podswietlona(kol, war, retailers) else tlo_domyslne
                draw.rectangle([x, y, x + szerkosci[i], y + wysokosc_wiersza], fill=tlo, outline=KOL_RAMKA)
                draw.text((x + padding, y + 8), str(war), font=font, fill=KOL_TEKST)
                x += szerkosci[i]
            y += wysokosc_wiersza

    img.save(sciezka_png)
    print(f"\n✓ Połączony zrzut zapisany: {sciezka_png}")

def main():
    print("=== QLA — Łączenie zrzutów ekranu ===\n")

    pliki = wybierz_pliki_json()
    if not pliki:
        return

    sekcje = []
    for plik_json in pliki:
        sciezka_json = os.path.join(OUTPUT_FOLDER, plik_json)
        with open(sciezka_json, "r", encoding="utf-8") as f:
            dane = json.load(f)
        sekcje.append({
            "fraza": dane["fraza"],
            "wyniki": dane["wyniki"],
            "retailers": dane.get("retailers", []),
        })

    nazwy_fraz = "_".join(re.sub(r'[^\w\-]', '_', s["fraza"]) for s in sekcje)
    if len(nazwy_fraz) > 80:
        nazwy_fraz = nazwy_fraz[:80]
    sciezka_png = os.path.join(OUTPUT_FOLDER, f"polaczony_{nazwy_fraz}.png")

    generuj_obraz_polaczony(sekcje, sciezka_png)

if __name__ == "__main__":
    main()
