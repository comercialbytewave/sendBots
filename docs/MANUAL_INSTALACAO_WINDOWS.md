# Manual de Instalacao e Configuracao no Windows

## 1. Instalar

1. Execute `SendBots-Setup-0.1.0.exe`.
2. Confirme a permissao do Controle de Conta de Usuario do Windows.
3. Siga o assistente e mantenha a pasta sugerida, normalmente
   `C:\Program Files\SendBots`.
4. Conclua a instalacao e abra o SendBots pelo Menu Iniciar ou pelo atalho da
   area de trabalho.

O SendBots aparece na lista de aplicativos instalados do Windows e possui
desinstalador proprio.

## 2. Configurar

Na aba `Configuracao`, informe:

- `URL base`: endereco da AlowChat, sem `/api/company/messages/whatsapp`.
- `Token Bearer`: token de autorizacao fornecido pela AlowChat.
- `Slug da loja`: identificador da empresa, por exemplo `hents-burg`.
- `Pasta monitorada`: pasta que recebera as notas e os boletos.
- `Mensagem`: texto enviado ao cliente.
- `Intervalo`, `Timeout` e `Tentativas`: parametros do monitoramento.
- `userId` e `queueId`: IDs opcionais da AlowChat.

Configure tambem as opcoes de assinatura, encerramento do ticket, espera pelo
par Nota Fiscal + Boleto, envio conjunto e uniao dos PDFs.

Clique em `Validar`. O aplicativo consulta:

```text
[URL base]/api/company/status/[Slug da loja]
Authorization: Bearer [Token Bearer]
```

Somente uma empresa com `status: true` pode salvar a configuracao e enviar
documentos. Depois da validacao, clique em `Salvar`.

## 3. Nome dos arquivos

Use exatamente um destes formatos:

```text
Nfe[NumeroNota]_[WhatsApp]_[ChaveAcesso].pdf
Boleto[NumeroBoleto]_[WhatsApp]_[CodigoBarras].pdf
```

Exemplos:

```text
Nfe31_558598146212_1234567489.pdf
Boleto31_558598146212_123456789.pdf
```

Quando `Aguardar nota + boleto` estiver ativo, os dois arquivos precisam ter o
mesmo WhatsApp no nome.

## 4. Iniciar e usar em background

Na aba `Operacao`, clique em `Iniciar monitoramento`. Ao minimizar, o SendBots
continua funcionando na area de notificacao, perto do relogio do Windows. De
dois cliques no icone para restaurar a janela.

Ao clicar no `X`, selecione:

- `Sim`: encerra o SendBots.
- `Nao`: mantem o SendBots rodando em background.

## 5. Logs e diagnostico

Os dados, o historico e o arquivo `sendbots.log` ficam na pasta de dados do
usuario do Windows. Para localizar o caminho exato, abra o Prompt de Comando na
pasta do programa e execute:

```text
SendBots.exe --paths
```

Erros comuns:

- `401` ou `403`: confira o Token Bearer.
- `404`: confira a URL base e o Slug da loja.
- Empresa inativa: a API retornou `status: false`; nenhum arquivo sera enviado.
- Arquivo invalido: confira o padrao do nome do PDF.
- Aguardando par: Nota Fiscal e Boleto precisam usar o mesmo WhatsApp.

## 6. Desinstalar

Abra `Configuracoes > Aplicativos > Aplicativos instalados`, procure por
`SendBots` e clique em `Desinstalar`.
