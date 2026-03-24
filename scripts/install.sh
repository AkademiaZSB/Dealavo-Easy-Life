#!/bin/bash

echo "=== Instalator Dealavo Tools ==="

# Folder instalacji
INSTALL_DIR="$HOME/dealavo-tools"
mkdir -p "$INSTALL_DIR"

# Pobierz pliki z GitHuba
echo "Pobieranie plików..."
curl -fsSL "https://raw.githubusercontent.com/AkademiaZSB/Dealavo-Easy-Life/main/QL.py" -o "$INSTALL_DIR/QL.py"
curl -fsSL "https://raw.githubusercontent.com/AkademiaZSB/Dealavo-Easy-Life/main/QLE.py" -o "$INSTALL_DIR/QLE.py"

# Instaluj Pillow
echo "Instalowanie Pillow..."
pip3 install Pillow --quiet

# Utwórz folder wejściowy
mkdir -p "$HOME/Downloads/QL"

# Dodaj aliasy
SHELL_RC="$HOME/.bashrc"
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
fi

if ! grep -q "alias ql=" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "alias ql=\"python3 $INSTALL_DIR/QL.py\"" >> "$SHELL_RC"
    echo "alias qle=\"python3 $INSTALL_DIR/QLE.py\"" >> "$SHELL_RC"
    echo "Aliasy dodane do $SHELL_RC"
else
    echo "Aliasy już istnieją — pomijam."
fi

echo ""
echo "=== Gotowe! ==="
echo "Wpisz: source ~/${SHELL_RC##*/}  (lub zrestartuj terminal)"
echo "Następnie używaj: ql  lub  qle"
