# Build do Instalador Windows

Este projeto gera um instalador `.exe` com assistente de instalacao usando Inno Setup.

## Resultado esperado

Arquivo final:

```text
dist\installer\SendBots-Setup-0.1.0.exe
```

Ao executar esse instalador no Windows:

- abre um wizard de instalacao;
- solicita permissao de administrador;
- instala em `C:\Program Files\SendBots`;
- cria grupo no Menu Iniciar;
- permite criar atalho na Area de Trabalho;
- registra o SendBots em `Aplicativos instalados` / `Programas e Recursos`;
- cria desinstalador do Windows.

## Requisitos na maquina Windows de build

- Python 3.11 ou superior.
- Inno Setup 6.

Download do Inno Setup:

```text
https://jrsoftware.org/isdl.php
```

## Comando para gerar o instalador

Abra o PowerShell na pasta do projeto:

```powershell
cd "C:\caminho\para\SendBots"
.\scripts\build_windows.ps1 -Installer
```

## Onde pegar o instalador

Depois do build:

```text
dist\installer\SendBots-Setup-0.1.0.exe
```

Esse e o arquivo que deve ser enviado para o cliente instalar no Windows.

## Observacao importante

O instalador Windows precisa ser gerado em uma maquina Windows. O PyInstaller nao gera `.exe` Windows corretamente a partir do Linux.

