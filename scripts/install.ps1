# Instalator Dealavo Tools - Windows
Write-Host "=== Instalator Dealavo Tools ===" -ForegroundColor Cyan

# Folder instalacji
$InstallDir = "$HOME\dealavo-tools"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# Pobierz pliki z GitHuba
Write-Host "Pobieranie plikow..."
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/AkademiaZSB/Dealavo-Easy-Life/main/QL.py" -OutFile "$InstallDir\QL.py"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/AkademiaZSB/Dealavo-Easy-Life/main/QLE.py" -OutFile "$InstallDir\QLE.py"

# Instaluj Pillow
Write-Host "Instalowanie Pillow..."
pip install Pillow --quiet

# Utwórz folder wejściowy
New-Item -ItemType Directory -Force -Path "$HOME\Downloads\QL" | Out-Null

# Utwórz pliki .bat dla komend ql i qle
$BatDir = "$HOME\dealavo-tools"
Set-Content -Path "$BatDir\ql.bat" -Value "@echo off`npython `"$InstallDir\QL.py`" %*"
Set-Content -Path "$BatDir\qle.bat" -Value "@echo off`npython `"$InstallDir\QLE.py`" %*"

# Dodaj folder do PATH (dla bieżącego użytkownika)
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($CurrentPath -notlike "*dealavo-tools*") {
    [Environment]::SetEnvironmentVariable("PATH", "$CurrentPath;$BatDir", "User")
    Write-Host "Dodano do PATH."
} else {
    Write-Host "PATH juz zawiera folder — pomijam."
}

Write-Host ""
Write-Host "=== Gotowe! ===" -ForegroundColor Green
Write-Host "Zrestartuj terminal, nastepnie uzywaj: ql  lub  qle"
