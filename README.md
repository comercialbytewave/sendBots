# SendBots

Aplicativo desktop em Python para monitorar uma pasta de PDFs, identificar Notas Fiscais e Boletos pelo padrao de nomenclatura e enviar os arquivos pela API AlowChat. Apos o sucesso, os PDFs recebem a marcacao `ENV` e sao movidos para a subpasta `Enviados`.

O aplicativo tambem pode juntar Nota Fiscal e Boleto em um unico PDF antes do envio quando a opcao estiver habilitada.

Ao minimizar, o app continua rodando na area de notificacao do Windows ou Linux. Um duplo clique no icone restaura a janela.

## Executar em desenvolvimento

No Linux, prefira rodar com ambiente virtual local:

```bash
chmod +x scripts/run_local_linux.sh
./scripts/run_local_linux.sh
```

Ou manualmente:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m sendbots
```

Se ja estiver com as dependencias instaladas:

```bash
python3 -m sendbots
```

Ver caminhos de banco e logs:

```bash
python3 -m sendbots --paths
```

Executar uma varredura com a configuracao salva:

```bash
python3 -m sendbots --scan-once
```

## Executar testes

```bash
python3 -m unittest discover -s tests
```

## Gerar executavel Windows

Veja o [manual de instalacao no Windows](docs/MANUAL_INSTALACAO_WINDOWS.md),
o [manual de uso](docs/MANUAL_USO.md) e os arquivos em `packaging/`.

```powershell
.\scripts\build_windows.ps1 -Installer
```

## Gerar executavel Linux

```bash
chmod +x scripts/build_linux.sh scripts/install_linux.sh scripts/uninstall_linux.sh
./scripts/build_linux.sh
./scripts/install_linux.sh
```

O executavel Linux fica em:

```text
dist/SendBots/SendBots
```
