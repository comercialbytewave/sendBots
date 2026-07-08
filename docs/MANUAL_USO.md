# Manual de Uso - SendBots

## 1. Finalidade

O SendBots monitora uma pasta local, identifica arquivos PDF de Nota Fiscal e Boleto, envia os documentos pela API AlowChat e renomeia arquivos enviados com `ENV`.

## 2. Padrao dos arquivos

Nota Fiscal:

```text
Nfe[NumeroNota]_[WhatsApp]_[ChaveAcesso].pdf
```

Exemplo:

```text
Nfe0001_5585998146212_12312313212315.pdf
```

Boleto:

```text
Boleto[NumeroBoleto]_[WhatsApp]_[CodigoBarras].pdf
```

Exemplo:

```text
Boleto0001_5585998146212_123123123123.pdf
```

Depois do envio:

```text
Nfe0001_5585998146212_12312313212315_ENV.pdf
Boleto0001_5585998146212_123123123123_ENV.pdf
```

## 3. Configuracao

Na aba `Configuracao`, preencher:

- URL base AlowChat.
- Token Bearer.
- Pasta monitorada.
- Mensagem.
- Intervalo de varredura, minimo de 10 segundos.
- Timeout.
- Tentativas.
- `userId`, se aplicavel.
- `queueId`, se aplicavel.
- Assinar mensagem.
- Encerrar ticket.
- Aguardar nota + boleto.
- Enviar anexos juntos.
- Juntar nota e boleto em um PDF.

O endpoint usado pelo aplicativo sera:

```text
[URL base]/api/messages/send
```

Quando `Juntar nota e boleto em um PDF` estiver ativo, o aplicativo cria um PDF temporario contendo primeiro a Nota Fiscal e depois o Boleto. Apenas esse PDF unico e enviado para a API. Depois do sucesso, os arquivos originais sao renomeados com `ENV` e o PDF temporario e removido.

## 4. Operacao

Na aba `Operacao`:

- `Iniciar monitoramento`: inicia a verificacao automatica da pasta.
- `Parar`: interrompe o monitoramento.
- `Executar varredura agora`: executa uma verificacao manual.
- `Abrir pasta`: abre a pasta configurada.

Ao minimizar a janela, o SendBots continua em background na area de notificacao do Windows ou Linux. Para abrir novamente, de dois cliques no icone do SendBots ou use a opcao `Abrir SendBots` no menu do icone.

Ao clicar no `X` para fechar, o aplicativo pergunta se deve encerrar o programa ou continuar rodando em background. Para encerrar de verdade pela bandeja, use a opcao `Sair` no icone da area de notificacao.

## 5. Historico

A aba `Historico` exibe os ultimos eventos registrados:

- enviados;
- erros;
- arquivos invalidos;
- arquivos ignorados.

Quando a opcao `Aguardar nota + boleto` estiver ativa, o envio so acontece quando existir uma Nota Fiscal e um Boleto com o mesmo WhatsApp no nome do arquivo. Se os numeros forem diferentes, o aplicativo registra dois grupos separados e informa qual arquivo esta faltando em cada grupo.

Exemplo:

```text
Boleto31_558598146212_123456789.pdf
nfe31_5585981462121_1234567489.pdf
```

Nesse caso os arquivos nao formam par, porque os WhatsApps sao diferentes:

```text
558598146212
5585981462121
```

Os logs sao salvos em `sendbots.log` dentro do diretorio de dados do usuario.

Se aparecer `Arquivo invalido ignorado`, confira o caminho exibido no log. O aplicativo analisa todos os PDFs dentro da pasta monitorada. PDFs soltos nessa pasta, como `saida.pdf` ou `saída.pdf`, serao ignorados por nao seguirem o padrao de Nota Fiscal ou Boleto.

## 6. Executar em desenvolvimento

No Linux, use ambiente virtual local para evitar o erro `externally-managed-environment`:

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

Se a opcao `Juntar nota e boleto em um PDF` mostrar erro de `pypdf`, o aplicativo foi aberto por um Python sem a dependencia. Feche o app e abra usando:

```bash
./scripts/run_local_linux.sh
```

Se estiver usando a versao instalada no Linux, gere e instale novamente:

```bash
./scripts/build_linux.sh
./scripts/install_linux.sh
```

Comandos auxiliares:

```bash
python3 -m sendbots --paths
python3 -m sendbots --scan-once
```

## 7. Executar no Windows e no Linux

O codigo do SendBots e multiplataforma. A interface desktop usa Tkinter e o empacotamento usa PyInstaller.

Importante: executaveis PyInstaller devem ser gerados no mesmo sistema operacional de destino:

- Para Windows, gerar o `.exe` em uma maquina Windows.
- Para Linux, gerar o binario em uma maquina Linux.

No Linux, a area de notificacao depende do ambiente grafico. Em alguns desktops GNOME, pode ser necessario habilitar suporte a tray/appindicator.

## 8. Gerar executavel Windows

Para gerar um instalador `.exe` com wizard de instalacao, use uma maquina Windows com Python 3.11+ e Inno Setup 6 instalado.

No PowerShell:

```powershell
cd "C:\caminho\para\SendBots"
.\scripts\build_windows.ps1 -Installer
```

O instalador sera gerado em:

```text
dist\installer\SendBots-Setup-0.1.0.exe
```

Ao instalar, o SendBots fica em:

```text
C:\Program Files\SendBots
```

E tambem aparece em:

```text
Menu Iniciar > SendBots
Aplicativos instalados / Programas e Recursos
```

Documentacao detalhada:

```text
docs/BUILD_WINDOWS_INSTALLER.md
```

## 9. Gerar executavel Linux

Dependencias recomendadas no Linux:

```bash
sudo apt install python3 python3-pip python3-tk
```

Gerar o binario:

```bash
chmod +x scripts/build_linux.sh scripts/install_linux.sh scripts/uninstall_linux.sh
./scripts/build_linux.sh
```

Executar sem instalar:

```bash
./dist/SendBots/SendBots
```

Instalar apenas para o usuario atual:

```bash
./scripts/install_linux.sh
```

Depois de instalado, executar pelo menu do sistema ou pelo comando:

```bash
sendbots
```

Desinstalar do usuario atual:

```bash
./scripts/uninstall_linux.sh
```

O build Linux tambem gera um pacote portatil:

```text
dist/linux/SendBots-linux.tar.gz
```

## 10. Dados locais

O aplicativo salva configuracao, historico e logs no diretorio de dados do usuario.

No Windows, normalmente:

```text
%APPDATA%\SendBots
```

No Linux:

```text
~/.local/share/sendbots
```
