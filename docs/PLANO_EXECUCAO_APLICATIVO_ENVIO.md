# Plano de Execucao - Aplicativo de Envio AlowChat

## 1. Objetivo

Implementar um aplicativo desktop instalavel, desenvolvido em Python, para monitorar uma pasta local configuravel, identificar notas fiscais e boletos gerados pelo ERP Ultrasyst, enviar os arquivos aos clientes via API AlowChat e renomear os arquivos enviados com a marcacao `ENV`.

O aplicativo deve ser entregue em formato executavel/instalador para uso operacional, sem exigir que o usuario final execute comandos Python manualmente.

## 2. Escopo Funcional

### 2.1 Monitoramento de arquivos

- Monitorar um diretorio local configuravel.
- Executar varreduras em intervalo configuravel, respeitando minimo de 10 segundos.
- Identificar arquivos PDF que sigam os padroes:
  - Nota Fiscal: `Nfe[NumeroNota]_[WhatsApp]_[ChaveAcesso].pdf`
  - Boleto: `Boleto[NumeroBoleto]_[WhatsApp]_[CodigoBarras].pdf`
- Relacionar nota fiscal e boleto pelo numero de WhatsApp presente no nome do arquivo.
- Ignorar arquivos ja marcados como enviados com `ENV`.
- Manter os arquivos na pasta apos o envio.
- Renomear arquivos enviados adicionando `ENV` ao final do nome base.

### 2.2 Envio pela API AlowChat

Endpoint padrao configuravel:

```text
[URL]/api/messages/send
```

Metodo:

```text
POST
```

Headers:

```text
Authorization: Bearer [token]
Content-Type: multipart/form-data
```

FormData:

```text
number: 558599999999
body: Message
userId: ID usuario ou ""
queueId: ID da fila ou ""
medias: arquivo
sendSignature: true/false
closeTicket: true/false
```

### 2.3 Configuracoes obrigatorias

O aplicativo deve permitir configurar, no minimo:

- URL base da API AlowChat.
- Token Bearer.
- Caminho da pasta monitorada.
- Intervalo de varredura/envio, com minimo de 10 segundos.
- Mensagem de envio customizada.
- `userId`.
- `queueId`.
- `sendSignature`.
- `closeTicket`.
- Timeout da requisicao.
- Quantidade de tentativas em caso de falha.
- Estrategia de envio:
  - enviar nota e boleto juntos quando a API aceitar multiplos arquivos;
  - ou enviar em chamadas separadas quando a API aceitar apenas um arquivo por campo `medias`.

### 2.4 Historico e auditoria

- Registrar logs locais de execucao.
- Registrar arquivos encontrados, enviados, ignorados e com erro.
- Registrar resposta HTTP da API, sem expor token completo nos logs.
- Registrar data/hora de envio.
- Manter historico consultavel pela interface ou arquivo local.

## 3. Premissas Tecnicas

- Linguagem: Python.
- Recomendacao: Python 3.11 ou superior para seguranca, bibliotecas atuais e empacotamento moderno.
- Observacao: o documento de requisitos cita Python 2.6, mas essa versao esta obsoleta e deve ser tratada como referencia legada, salvo restricao formal do ambiente do cliente.
- Empacotamento sugerido: PyInstaller para gerar executavel.
- Instalador sugerido:
  - Windows: Inno Setup ou NSIS.
  - Linux: binario PyInstaller com instalador local `.sh` e pacote portatil `.tar.gz`.
  - Alternativa simples: distribuicao de pasta executavel compactada, caso o cliente aceite.
- Interface desktop sugerida:
  - PySide6/PyQt6 para interface mais robusta;
  - ou Tkinter para reduzir dependencias.
- Armazenamento local sugerido:
  - SQLite para historico e fila de envio;
  - arquivo `.json` ou `.toml` para configuracoes simples.

## 4. Arquitetura Proposta

### 4.1 Modulos

- `app/ui`: telas de configuracao, status, logs e operacao manual.
- `app/config`: leitura, validacao e persistencia das configuracoes.
- `app/watcher`: varredura periodica do diretorio.
- `app/parser`: validacao dos nomes de arquivos e extracao de numero, tipo e identificadores.
- `app/matcher`: agrupamento de Nota Fiscal e Boleto pelo WhatsApp.
- `app/alowchat`: cliente HTTP da API AlowChat.
- `app/sender`: fila, envio, retentativas e tratamento de erros.
- `app/renamer`: renomeacao segura com `ENV`.
- `app/storage`: historico local, status dos arquivos e logs.
- `app/packaging`: scripts de build do executavel e instalador.

### 4.2 Fluxo Principal

1. Usuario configura API, token, pasta, intervalo e parametros de envio.
2. Aplicativo valida as configuracoes.
3. Aplicativo inicia monitoramento da pasta.
4. Varredura identifica PDFs validos.
5. Arquivos ja enviados ou com `ENV` sao ignorados.
6. Arquivos sao agrupados pelo numero de WhatsApp.
7. Aplicativo monta o `multipart/form-data`.
8. Aplicativo envia a mensagem e anexos para AlowChat.
9. Em caso de sucesso, os arquivos enviados sao renomeados com `ENV`.
10. Em caso de erro, o evento e registrado e o envio entra em retentativa conforme configuracao.

## 5. Regras de Negocio

- O intervalo de varredura nao pode ser menor que 10 segundos.
- Apenas arquivos `.pdf` devem ser processados.
- O numero de WhatsApp deve ser extraido do segundo segmento do nome, separado por `_`.
- Arquivos fora do padrao devem ser ignorados e registrados como invalidos.
- Arquivos com `ENV` no final do nome base nao devem ser reenviados.
- A renomeacao deve ocorrer somente apos confirmacao de sucesso da API.
- O token deve ser armazenado de forma protegida quando possivel, ou ao menos mascarado na interface e nos logs.
- Se existir apenas Nota Fiscal ou apenas Boleto, a regra deve ser configuravel:
  - aguardar par completo;
  - ou enviar arquivo individual.
- Se o arquivo estiver em uso pelo ERP, o aplicativo deve aguardar a proxima varredura antes de processar.

## 6. Sprints de Implementacao

## Sprint 0 - Preparacao e Validacao Tecnica

### Objetivo

Confirmar requisitos, tecnologia, formato de entrega e detalhes da API AlowChat antes do desenvolvimento principal.

### Atividades

- Validar se o ambiente alvo e Windows, Linux ou ambos.
- Validar se o instalador deve ser `.exe`, `.msi` ou pasta executavel.
- Validar versao Python a ser adotada.
- Validar com AlowChat se `medias` aceita multiplos arquivos na mesma requisicao.
- Validar se `sendSignature` e `closeTicket` devem ser enviados como booleanos reais ou texto `true/false`.
- Validar exemplos de resposta de sucesso e erro da API.
- Definir layout basico da interface.
- Criar backlog tecnico inicial.

### Entregaveis

- Decisoes tecnicas registradas.
- Contrato de API confirmado.
- Estrutura inicial do projeto.

### Checks de Conclusao

- [ ] Ambiente alvo documentado.
- [ ] Formato do instalador definido.
- [ ] Versao Python definida.
- [ ] Contrato da API AlowChat confirmado.
- [ ] Regra de envio de multiplos anexos confirmada.
- [ ] Estrutura inicial do repositorio aprovada.

## Sprint 1 - Base do Projeto e Configuracoes

### Objetivo

Criar a base do aplicativo, persistencia de configuracoes e validacoes iniciais.

### Atividades

- Criar estrutura de pastas da aplicacao.
- Criar modelo de configuracao.
- Criar tela ou formulario de configuracao.
- Implementar persistencia local das configuracoes.
- Validar URL base, token, pasta, intervalo, `userId`, `queueId`, `sendSignature` e `closeTicket`.
- Mascarar token na interface e logs.
- Implementar teste de conexao com a API, se houver endpoint disponivel.

### Entregaveis

- Aplicativo abre localmente.
- Configuracoes podem ser salvas, carregadas e validadas.

### Checks de Conclusao

- [ ] Aplicativo inicia sem erro.
- [ ] Pasta monitorada pode ser selecionada.
- [ ] Intervalo menor que 10 segundos e bloqueado.
- [ ] Token e salvo e exibido de forma mascarada.
- [ ] Configuracoes persistem apos fechar e abrir o aplicativo.
- [ ] Logs nao exibem token completo.

## Sprint 2 - Leitura, Parser e Agrupamento de Arquivos

### Objetivo

Implementar a deteccao dos arquivos, validacao de nomenclatura e agrupamento por WhatsApp.

### Atividades

- Implementar varredura manual da pasta.
- Implementar parser para nomes `Nfe...` e `Boleto...`.
- Extrair numero de WhatsApp, numero da nota, chave de acesso, numero do boleto e codigo de barras.
- Ignorar arquivos com `ENV`.
- Detectar arquivos invalidos.
- Agrupar pares Nota Fiscal + Boleto pelo numero de WhatsApp.
- Criar testes unitarios para os principais padroes de nome.

### Entregaveis

- Lista de arquivos validos, invalidos e pendentes.
- Agrupamento de anexos por numero de WhatsApp.

### Checks de Conclusao

- [ ] `Nfe0001_5585998146212_12312313212315.pdf` e reconhecido como nota.
- [ ] `Boleto0001_5585998146212_123123123123.pdf` e reconhecido como boleto.
- [ ] O numero `5585998146212` e extraido corretamente.
- [ ] Arquivos com `ENV` sao ignorados.
- [ ] Arquivos fora do padrao sao registrados como invalidos.
- [ ] Pares sao agrupados pelo mesmo numero de WhatsApp.
- [ ] Testes de parser passam.

## Sprint 3 - Cliente AlowChat e Envio Manual

### Objetivo

Implementar o cliente HTTP da API AlowChat e permitir envio controlado/manual para validacao.

### Atividades

- Criar modulo cliente da API.
- Montar requisicao `multipart/form-data`.
- Enviar `number`, `body`, `userId`, `queueId`, `medias`, `sendSignature` e `closeTicket`.
- Implementar timeout.
- Implementar tratamento de respostas HTTP.
- Implementar mascaramento de dados sensiveis nos logs.
- Criar envio manual de um grupo de arquivos selecionado.
- Criar testes com mock da API.

### Entregaveis

- Envio manual funcionando contra ambiente de teste ou mock.
- Tratamento de sucesso e falha.

### Checks de Conclusao

- [ ] Requisicao usa `POST`.
- [ ] Header `Authorization: Bearer` e enviado corretamente.
- [ ] FormData contem todos os campos obrigatorios.
- [ ] Arquivo PDF e enviado no campo `medias`.
- [ ] Erros 400, 401, 403, 404 e 500 sao tratados.
- [ ] Timeout e tratado sem travar interface.
- [ ] Testes com mock da API passam.

## Sprint 4 - Monitoramento Automatico e Fila de Envio

### Objetivo

Automatizar o ciclo de varredura e envio, com fila local e retentativas.

### Atividades

- Implementar monitoramento automatico por intervalo.
- Criar fila de envio local.
- Evitar processamento duplicado durante uma mesma execucao.
- Detectar arquivos ainda em gravacao.
- Implementar retentativas configuraveis.
- Implementar status por item: pendente, enviando, enviado, erro, ignorado.
- Garantir que falhas nao interrompam o monitoramento.

### Entregaveis

- Envio automatico em funcionamento.
- Fila com status operacional.

### Checks de Conclusao

- [ ] Monitoramento respeita o intervalo configurado.
- [ ] Aplicativo nao processa o mesmo arquivo simultaneamente.
- [ ] Arquivo em uso nao e enviado ate estar disponivel.
- [ ] Falha de um envio nao interrompe os demais.
- [ ] Retentativas seguem a configuracao.
- [ ] Status da fila e atualizado corretamente.

## Sprint 5 - Renomeacao, Auditoria e Historico

### Objetivo

Concluir o ciclo apos sucesso da API, renomeando arquivos e registrando historico rastreavel.

### Atividades

- Implementar renomeacao segura com sufixo `ENV`.
- Definir formato final do nome:
  - exemplo: `Nfe0001_5585998146212_12312313212315_ENV.pdf`
  - exemplo: `Boleto0001_5585998146212_123123123123_ENV.pdf`
- Tratar conflito caso arquivo `_ENV.pdf` ja exista.
- Registrar historico local de envios.
- Criar tela ou consulta de historico.
- Exportar logs, se necessario.

### Entregaveis

- Arquivos enviados renomeados corretamente.
- Historico local confiavel.

### Checks de Conclusao

- [ ] Arquivos sao renomeados somente apos sucesso da API.
- [ ] O arquivo original permanece na mesma pasta.
- [ ] Arquivos ja renomeados com `ENV` nao sao reenviados.
- [ ] Conflitos de nome sao tratados.
- [ ] Historico exibe data/hora, numero, arquivos, status e retorno resumido.
- [ ] Logs permitem diagnosticar falhas sem expor token.

## Sprint 6 - Interface Operacional

### Objetivo

Entregar uma interface clara para configuracao, acompanhamento e operacao diaria.

### Atividades

- Criar tela principal com status do monitoramento.
- Criar acoes iniciar, pausar e parar monitoramento.
- Exibir pasta monitorada e proxima varredura.
- Exibir fila atual e ultimos envios.
- Exibir alertas de configuracao incorreta.
- Exibir erros recentes.
- Criar acao de reprocessar item com erro.
- Criar acao de abrir pasta monitorada.

### Entregaveis

- Interface pronta para uso operacional.

### Checks de Conclusao

- [ ] Usuario consegue configurar o aplicativo pela interface.
- [ ] Usuario consegue iniciar e parar o monitoramento.
- [ ] Usuario consegue ver arquivos pendentes, enviados e com erro.
- [ ] Usuario consegue reprocessar falhas.
- [ ] Interface permanece responsiva durante envios.
- [ ] Mensagens de erro sao compreensiveis para usuario operacional.

## Sprint 7 - Empacotamento e Instalador

### Objetivo

Gerar executavel e instalador para distribuicao.

### Atividades

- Configurar build com PyInstaller.
- Definir icone e nome do aplicativo.
- Gerar executavel.
- Gerar instalador Windows.
- Incluir arquivos necessarios de configuracao inicial.
- Criar processo de atualizacao manual.
- Testar instalacao em maquina limpa.

### Entregaveis

- Executavel do aplicativo.
- Instalador.
- Instrucoes de instalacao e desinstalacao.

### Checks de Conclusao

- [ ] Build gera executavel sem erro.
- [ ] Instalador instala o aplicativo corretamente.
- [ ] Aplicativo abre apos instalacao.
- [ ] Configuracoes sao salvas em local adequado do usuario.
- [ ] Desinstalacao remove o aplicativo sem apagar dados do usuario sem confirmacao.
- [ ] Aplicativo funciona em maquina sem Python instalado.

## Sprint 8 - Testes Integrados, Homologacao e Entrega

### Objetivo

Validar o aplicativo em fluxo real com arquivos de exemplo, API AlowChat e ambiente do cliente.

### Atividades

- Executar testes funcionais completos.
- Testar envio com Nota Fiscal e Boleto.
- Testar envio com apenas um arquivo, conforme regra configurada.
- Testar falha de token invalido.
- Testar falha de URL incorreta.
- Testar pasta vazia.
- Testar arquivos invalidos.
- Testar alto volume de arquivos.
- Ajustar bugs encontrados.
- Preparar documentacao final.

### Entregaveis

- Versao candidata a producao.
- Relatorio de homologacao.
- Manual rapido de uso.

### Checks de Conclusao

- [ ] Fluxo completo envia arquivos pela API.
- [ ] Arquivos enviados sao renomeados com `ENV`.
- [ ] Falhas sao registradas corretamente.
- [ ] Aplicativo recupera operacao apos reiniciar.
- [ ] Instalador validado no ambiente alvo.
- [ ] Manual de uso entregue.
- [ ] Cliente homologa o envio.

## 7. Checklist Geral por Execucao de Sprint

Antes de iniciar cada sprint:

- [ ] Confirmar objetivo da sprint.
- [ ] Revisar pendencias da sprint anterior.
- [ ] Confirmar ambiente de desenvolvimento.
- [ ] Confirmar se houve mudanca no contrato da API AlowChat.
- [ ] Confirmar arquivos de exemplo disponiveis.
- [ ] Criar ou atualizar branch de trabalho.

Durante a sprint:

- [ ] Implementar em incrementos pequenos.
- [ ] Registrar decisoes tecnicas relevantes.
- [ ] Manter configuracoes sensiveis fora do codigo fonte.
- [ ] Atualizar testes conforme funcionalidade criada.
- [ ] Validar comportamento com arquivos reais ou simulados.
- [ ] Revisar logs para garantir que nao exponham token.

Ao finalizar a sprint:

- [ ] Executar testes automatizados.
- [ ] Executar teste manual do fluxo alterado.
- [ ] Atualizar documentacao, quando necessario.
- [ ] Gerar evidencias de teste.
- [ ] Revisar criterios de aceite.
- [ ] Registrar bugs e riscos restantes.
- [ ] Planejar proxima sprint com base nos resultados.

## 8. Criterios de Aceite do Produto

- Aplicativo instalado por executavel/instalador.
- Aplicativo executa sem Python instalado na maquina do usuario.
- API AlowChat totalmente configuravel pela interface ou arquivo de configuracao.
- Pasta monitorada configuravel.
- Intervalo configuravel com minimo de 10 segundos.
- Mensagem de envio customizavel.
- Envio de PDF pelo endpoint configurado.
- Renomeacao com `ENV` apos envio confirmado.
- Logs e historico disponiveis.
- Falhas tratadas sem interromper o aplicativo.
- Token protegido ou mascarado.
- Usuario operacional consegue configurar, iniciar, acompanhar e diagnosticar envios.

## 9. Riscos e Contingencias

| Risco | Impacto | Contingencia |
| --- | --- | --- |
| Token AlowChat alterado ou expirado | Envios falham | Tela de configuracao permite atualizar token e testar conexao |
| API nao aceita multiplos arquivos em `medias` | Envio de nota e boleto pode falhar | Configurar estrategia para enviar arquivos separadamente |
| Pasta configurada incorretamente | Nenhum arquivo enviado | Validacao de existencia e permissao da pasta |
| Arquivo ainda sendo gravado pelo ERP | Envio incompleto ou erro | Verificar estabilidade/tamanho do arquivo antes do envio |
| Falha ao renomear arquivo | Arquivo pode ser reenviado | Registrar erro, bloquear reenvio pelo historico e permitir reprocessamento controlado |
| Maquina sem permissao de escrita | Configuracao e logs falham | Usar diretorio de dados do usuario e validar permissoes |
| API fora do ar ou bloqueada | Fila acumula | Retentativas, historico e status claro para o usuario |

## 10. Pendencias de Confirmacao

- Confirmar sistemas operacionais finais: Windows, Linux ou ambos.
- Confirmar formato do instalador desejado.
- Confirmar se o campo `medias` aceita mais de um arquivo na mesma requisicao.
- Confirmar se `userId` e `queueId` podem ficar vazios em todos os cenarios.
- Confirmar se o envio deve aguardar sempre o par Nota Fiscal + Boleto.
- Confirmar texto padrao da mensagem.
- Confirmar se deve existir login local no aplicativo ou apenas configuracao protegida.
- Confirmar se o aplicativo deve iniciar automaticamente com o Windows.
