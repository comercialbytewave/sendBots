param(
    [switch]$Installer
)

$ErrorActionPreference = "Stop"

python -m pip install --upgrade pyinstaller pypdf pystray Pillow
pyinstaller packaging/sendbots.spec

if ($Installer) {
    $iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    $isccPath = $null
    if ($iscc) {
        $isccPath = $iscc.Source
    }

    if (-not $iscc) {
        $candidates = @(
            "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
            "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
        )
        foreach ($candidate in $candidates) {
            if (Test-Path $candidate) {
                $isccPath = $candidate
                break
            }
        }
    }

    if (-not $isccPath) {
        throw "Inno Setup nao encontrado. Instale o Inno Setup 6 em https://jrsoftware.org/isdl.php e rode novamente."
    }

    & $isccPath packaging/installer.iss
    Write-Host "Instalador gerado em: dist\installer\SendBots-Setup-0.1.0.exe"
}

Write-Host "Build concluido."
