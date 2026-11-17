# Citizen Assist AI

Assistente de terminal, feito em Python, que orienta **jovens que acabaram de completar 18 anos** sobre documentos e obrigações dessa fase da vida. Ele responde apenas com o que está em uma base de conhecimento verificada, mostra a **fonte oficial** e a **data de verificação** de cada orientação, avisa que **não é um canal oficial** e **não coleta dados pessoais**.

Projeto da Global Solution 2026.2 (desafio CitizenTech) · Pensamento Computacional e Automação com Python · FIAP · 1º ano de Ciência da Computação.

## Integrantes

| Nome | RM |
|---|---|
| Wendel Rezende | 573126 |
| Daniel Alejandro | 573075 |
| Arthur Araújo | 573308 |

## Público e problema

**Público atendido:** pessoas que acabaram de completar 18 anos.

**Problema:** nessa idade surgem várias tarefas ao mesmo tempo: criar a conta gov.br, emitir a Carteira de Identidade Nacional (CIN), tirar o passaporte, fazer o alistamento militar (obrigatório para homens), tirar o título de eleitor, acessar a Carteira de Trabalho Digital (CTPS), tirar a primeira CNH e abrir uma conta bancária própria. A informação existe, mas está espalhada, em linguagem técnica e misturada com páginas que parecem oficiais e não são. O Citizen Assist AI reúne essas orientações em um só lugar, em linguagem simples, sempre com a fonte oficial.

## ODS relacionados

- **ODS 16 (Paz, justiça e instituições eficazes):** acesso público à informação e a serviços do Estado, com fonte rastreável.
- **ODS 10 (Redução das desigualdades):** facilita o acesso a documentos e serviços para quem não sabe por onde começar.
- **ODS 8 (Trabalho decente e crescimento econômico):** orienta sobre a Carteira de Trabalho Digital, a conta bancária e a habilitação, etapas ligadas ao primeiro emprego.

## O que o assistente faz

- Responde **perguntas em texto livre** por uma busca com pontuação, informando o **nível de confiança** (ALTA ou MÉDIA).
- Permite **navegar por categorias**, com "0 para voltar" em todas as telas.
- Mostra, em toda resposta: documentos necessários, onde ir, **fonte**, **data de verificação** e o aviso de que o assistente não é canal oficial.
- **Recusa e não registra** perguntas com dados pessoais (8 ou mais dígitos, ou `@`).
- Trata entradas inválidas (opção fora da faixa, letras, resposta vazia, `s/n` inválido) sem encerrar o programa.
- **Registra cada atendimento** em `data/historico.json`, calcula **indicadores** e **exporta um CSV**.

## Como executar

Requisitos: **Python 3** (desenvolvido com o Python 3.14). Não há bibliotecas externas (apenas `json`, `csv`, `time` e `datetime`, da biblioteca padrão).

```
git clone https://github.com/<usuario>/citizen-assist-ai.git
cd citizen-assist-ai
python main.py
```

Menu principal:

```
 1 - Fazer uma pergunta
 2 - Navegar por categorias
 3 - Ver indicadores
 4 - Exportar atendimentos (CSV)
 0 - Sair
```

Ao sair pelo `0`, o assistente pede uma **nota de facilidade de uso (1 a 5)** e exporta o CSV.

## Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── main.py                  # menu principal
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # normalizar() e classe BaseConhecimento
├── assistente.py            # classe Assistente
└── data/
    ├── base_conhecimento.json   # as 10 orientações (dados)
    ├── historico.json           # atendimentos registrados
    └── atendimentos.csv         # exportação dos atendimentos
```

## Arquitetura: classes e composição

```
Assistente
└── base: BaseConhecimento
    └── orientacoes: [Orientacao, Orientacao, ...]
```

| Classe | O que representa | Atributos | Métodos |
|---|---|---|---|
| `Orientacao` | Uma informação da base (um registro do JSON) | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()` |
| `BaseConhecimento` | O conjunto de todas as orientações | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | Quem conversa com o cidadão | nome, base, historico (e caminho_historico) | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()` (mais métodos de apoio) |

Fluxo principal: `main.py` cria a `BaseConhecimento`, chama `carregar()` (que lê o JSON e cria um objeto `Orientacao` por registro com `Orientacao(**dicionario)`) e entrega a base ao `Assistente`.

## Base de conhecimento

Arquivo `data/base_conhecimento.json`: uma lista de dicionários, um por orientação, com os campos `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte` e `verificado_em`.

- **10 orientações** em **3 categorias**: *Identidade e conta digital*, *Deveres cívicos* e *Trabalho, mobilidade e finanças*.
- Todas com **fonte oficial** e a **data em que a equipe conferiu** a informação.
- Palavras-chave em minúsculas, sem acento e sem pontuação (mínimo de 3 por orientação).
- Respostas em linguagem simples, escritas somente com o que a fonte oficial informa.

## Regra de pontuação

A pergunta e as palavras-chave passam por `normalizar()` (minúsculas, sem acento, sem pontuação, com um espaço em cada ponta, para que a palavra-chave seja procurada como palavra inteira). Em seguida, cada orientação recebe pontos:

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação que aparece na pergunta | +3 (cada) |
| Palavra da pergunta, com 4 letras ou mais, que aparece no título | +1 (cada) |

| Melhor pontuação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras ou as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas ("Veja também"), desde que tenham 3 pontos ou mais.

**Exemplo:** na pergunta *"quero emitir cin"*, a orientação da CIN recebe +3 por `emitir cin`, +3 por `cin` e +1 porque `emitir` está no título: **7 pontos, confiança ALTA**.

## Exemplo de execução

```
Digite sua dúvida (0 para voltar): quero emitir cin

Confiança da resposta: ALTA (7 pontos)
>> Emitir a Carteira de Identidade Nacional (CIN) [Identidade e conta digital]
Agende o atendimento pelo app, site, autoatendimento ou WhatsApp do Poupatempo. Depois, compareça no dia, local e horário marcados. Vale para o estado de São Paulo.
Documentos necessários:
 - Certidão de nascimento
 - CPF
Onde: Poupatempo (estado de São Paulo)
Fonte: https://www.poupatempo.sp.gov.br/carta/D97C3844-A2D9-4C9E-B364-CB4FEB26A1FB (verificado em 2026-11-06)
AVISO: este assistente NÃO é um canal oficial.
Essa orientação respondeu sua dúvida? (s/n): s
Digite sua dúvida (0 para voltar): meu cpf é 123.456.789-00
Atenção: não digite CPF, telefone ou e-mail. Reescreva.
```

## Entradas inválidas, arquivos e dados pessoais

- **Menu e opções:** só são aceitos números dentro da faixa; letras, vazio e números fora da faixa mostram um aviso e repetem a pergunta.
- **Resposta `s/n`:** qualquer valor diferente de `s` ou `n` repete a pergunta.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Perguntas com 8 ou mais dígitos ou com `@` são recusadas e **não são guardadas** nem registradas.
- **Arquivos:** base ou histórico ausente, vazio ou corrompido não trava o programa; um registro da base com campos incorretos é ignorado com um aviso.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: data, origem (`pergunta` ou `categoria`), pergunta, id da orientação, se encontrou, se ajudou, tentativas, tempo em segundos e a nota de facilidade da sessão.

Indicadores calculados pelo menu 3:

| Indicador | Como é calculado |
|---|---|
| Resposta encontrada (%) | Atendimentos em que uma orientação foi encontrada ÷ total |
| Taxa de acerto (%) | Atendimentos em que a pessoa respondeu que a orientação ajudou ÷ total |
| Tempo médio para encontrar | Média do tempo dos atendimentos em que a pessoa foi ajudada |
| Tentativas por atendimento | Média de perguntas digitadas por atendimento (na navegação, 1 por orientação vista) |
| Facilidade de uso (1 a 5) | Média das notas dadas ao sair |
| Dúvidas sem solução | Perguntas dos atendimentos em que a pessoa não foi ajudada |

O CSV (`data/atendimentos.csv`) é gerado com `csv.DictWriter` a partir do histórico, ao sair ou pelo menu 4.

## Integrações com outras disciplinas

Nenhuma. Este projeto é independente e usa somente a biblioteca padrão do Python.

## Fontes consultadas

| id | Orientação | Fonte | Verificado em |
|---|---|---|---|
| 1 | Criar conta gov.br | https://www.gov.br/pt-br/servicos/criar-sua-conta-gov.br | 2026-11-06 |
| 2 | Aumentar o nível da conta gov.br | https://www.gov.br/pt-br/servicos/criar-sua-conta-gov.br | 2026-11-06 |
| 3 | Emitir a CIN | https://www.poupatempo.sp.gov.br/carta/D97C3844-A2D9-4C9E-B364-CB4FEB26A1FB | 2026-11-06 |
| 4 | Obter o passaporte | https://www.gov.br/pt-br/servicos/obter-passaporte-comum-para-brasileiro | 2026-11-06 |
| 5 | Alistamento militar obrigatório | https://www.gov.br/pt-br/servicos/alistar-se-no-servico-militar-obrigatorio | 2026-11-12 |
| 6 | Alistamento militar: perdi o prazo | https://www.gov.br/pt-br/servicos/alistar-se-no-servico-militar-obrigatorio | 2026-11-12 |
| 7 | Tirar o título de eleitor | https://www.tre-sp.jus.br/servicos-eleitorais/carta-de-servicos/primeiro-titulo-de-eleitor | 2026-11-12 |
| 8 | Carteira de Trabalho Digital (CTPS) | https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/Passo_a_Passo_CTPSDigital_APP_e_WEB.pdf | 2026-11-12 |
| 9 | Primeira CNH | https://www.gov.br/transportes/pt-br/cnh-do-brasil | 2026-11-12 |
| 10 | Conta bancária própria | https://www.bcb.gov.br/meubc/faqs/p/o-que-e-necessario-para-abrir-uma-conta-de-depositos | 2026-11-12 |

## Teste com usuários

> Preencher com os dados reais do teste. Não registrar nomes nem dados das pessoas.

- **Pessoas de fora da equipe:** [PREENCHER: mínimo 3]
- **Atendimentos realizados:** [PREENCHER: mínimo 10]

| Indicador | Resultado |
|---|---|
| Resposta encontrada (%) | [PREENCHER] |
| Taxa de acerto (%) | [PREENCHER] |
| Tempo médio para encontrar | [PREENCHER] s |
| Tentativas por atendimento | [PREENCHER] |
| Facilidade de uso (1 a 5) | [PREENCHER] |

**Dúvidas sem solução:** [PREENCHER: listar as perguntas, sem identificar ninguém]

**Melhoria feita a partir do teste:** [PREENCHER: por exemplo, a palavra-chave incluída na orientação X, e o que mudou na resposta da pergunta que antes não era encontrada]

Os arquivos `data/historico.json` e `data/atendimentos.csv` deste repositório são o registro desses atendimentos.

## Limitações

- A busca compara **palavras**: não entende sinônimos nem contexto. Ajustar uma palavra-chave pode melhorar uma pergunta e piorar outra. Exemplo medido: incluir `prazo do alistamento` na orientação 5 faz *"qual o prazo do alistamento"* ser encontrada, mas *"perdi o prazo do alistamento militar"* passa a dar 8 pontos para a orientação 5 contra 7 da orientação 6 (a errada vence).
- A base tem **10 orientações**; assuntos fora dela (por exemplo, CPF) resultam em "não encontrei".
- As orientações da **CIN** e do **título de eleitor** valem para o **estado de São Paulo**; em outros estados os procedimentos podem ser diferentes.
- O filtro de dados pessoais usa o limite de 8 dígitos: um número com 7 dígitos não é bloqueado.
- O indicador "resposta encontrada" inclui os atendimentos pela navegação por categorias, que sempre encontram uma orientação.
- A nota de facilidade é da sessão e é copiada para cada atendimento dela: sessões com mais atendimentos pesam mais na média.
- As informações podem mudar. Confira sempre a fonte indicada. **Este assistente não é um canal oficial.**

## Vídeo técnico

[PREENCHER: link do vídeo no YouTube, não listado]

## Uso de ferramentas de IA

A equipe usou o Claude (Anthropic) como guia de estudo e revisão durante o desenvolvimento. O código foi digitado, testado e é explicado pela própria equipe, e o conteúdo da base de conhecimento foi conferido pela equipe nas páginas oficiais.
