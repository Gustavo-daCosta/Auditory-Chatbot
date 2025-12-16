# 🏢 Chatbot de Auditoria - Dunder Mifflin

Sistema de auditoria inteligente desenvolvido para investigar fraudes, verificar compliance e responder perguntas sobre gastos corporativos na filial de Scranton da Dunder Mifflin.



https://github.com/user-attachments/assets/e721473d-3541-4b8d-b473-15d63395bb08



## 📚 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Como Executar](#-como-executar)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Troubleshooting](#-troubleshooting)
- [Vídeo de Demonstração](#-vídeo-de-demonstração)

## 📋 Sobre o Projeto

Este é um **Agente Inteligente Orquestrador** que utiliza LangChain + FAISS + Google Gemini para resolver os três níveis do desafio de auditoria proposto por Toby Flenderson:

1. **Nível 1**: Chatbot de Compliance (RAG sobre política de compliance)
2. **Nível 2**: Investigação de Conspirações (Busca semântica em emails)
3. **Nível 3**: Auditoria Contextual (Cruzamento de emails + transações bancárias)

## 🏗️ Arquitetura do Sistema

### Visão Geral - Arquitetura Multi-Agente

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUÁRIO                                 │
│                    (Interface CLI)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT                             │
│              (Coordenador Principal)                            │
│              LangChain + Gemini 2.0                             │
│                                                                 │
│  Ciclo: Thought → Action → Observation → ... → Final Answer    │
└────┬────────────────┬────────────────┬───────────────────────────┘
     │                │                │
     ▼                ▼                ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│ POLICY   │    │CONSPIRACY│    │COMPLIANCE│
│  AGENT   │    │  AGENT   │    │  AGENT   │
│          │    │          │    │          │
│📋 Regras │    │🕵️ Emails │    │💰 Gastos │
└────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │
     ▼               ▼               ▼
┌─────────┐    ┌─────────┐    ┌─────────┐
│  FAISS  │    │  FAISS  │    │Pandas DF│
│compliance    │ emails  │    │   CSV   │
│  Index  │    │  Index  │    │  Data   │
└─────────┘    └─────────┘    └─────────┘
```

> 📖 **Detalhes**: Veja [ARQUITETURA_AGENTES.md](ARQUITETURA_AGENTES.md) para documentação completa da arquitetura multi-agente

### Componentes Principais

#### 1. **Camada de Ingestão** (`src/ingest_data.py`)
- **Função**: Processa e armazena documentos no FAISS
- **Índices**:
  - `compliance`: Política de compliance dividida em chunks de 500 caracteres
  - `emails`: Emails internos divididos em chunks de 1000 caracteres
- **Embeddings**: Google Generative AI Embeddings (`models/embedding-001`)

#### 2. **Camada de Agentes Especializados** (`src/agents/`)

##### 📋 **Policy Agent** (`policy_agent.py`)
- **Especialidade**: Políticas e regras corporativas
- **Fonte**: Índice FAISS `compliance`
- **Ferramenta**: `policy_retriever`
- **Uso**: Consultar regras, limites de gastos, alçadas de aprovação
- **Exemplo**: "Qual o limite para jantares com cliente?"

##### 🕵️ **Conspiracy Agent** (`conspiracy_agent.py`)
- **Especialidade**: Investigação de comunicações internas
- **Fonte**: Índice FAISS `emails`
- **Ferramenta**: `email_search`
- **Uso**: Detectar conversas suspeitas, conspirações, planos fraudulentos
- **Exemplo**: "Michael está tramando contra Toby?"

##### 💰 **Compliance Agent** (`compliance_agent.py`)
- **Especialidade**: Auditoria de transações financeiras
- **Fonte**: DataFrame CSV `transacoes_bancarias.csv`
- **Ferramenta**: `csv_analysis`
- **Capabilities**: Buscar por valor, funcionário, categoria, análises estatísticas
- **Exemplo**: "Quais transações acima de $500?"

#### 3. **Camada de Orquestração** (`src/agents/orchestrator_agent.py`)

##### 🎯 Agente Orquestrador
- **LLM**: Google Gemini 2.0 Flash Exp
- **Temperature**: 0 (determinístico)
- **Framework**: LangChain `create_react_agent`
- **Prompt Engineering**: 
  - Persona: "Toby Flenderson Jr., Agente de Auditoria"
  - Instruções para multi-hop reasoning
  - Obrigação de citar fontes e evidências

**Fluxo de Raciocínio (Loop de Orquestração)**:
```
1. Thought:   "O usuário quer saber se pode gastar $200 em jantar"
2. Action:    policy_retriever
3. Input:     "limite jantar cliente refeição"
4. Observation: "Jantares limitados a $150 por pessoa..."
5. Thought:   "Agora sei que o limite é $150"
6. Final Answer: "Não pode. Política limita a $150."
```

#### 4. **Camada de Interface** (`src/main.py`)
- Interface CLI interativa
- Comandos: `help`, `demo`, `clear`, `sair`
- Tratamento de erros amigável
- Modo demo para demonstração dos 3 níveis

### Fluxo de Execução por Nível

#### 📘 Nível 1: Chatbot de Compliance
```
Usuário: "Posso gastar $200 em um jantar?"
   ↓
Agente: Invoca policy_retriever_tool
   ↓
FAISS: Retorna chunks relevantes da política
   ↓
Agente: Analisa e responde "Não, limite é $150"
```

#### 📘 Nível 2: Investigação de Emails
```
Usuário: "Michael está conspirando contra Toby?"
   ↓
Agente: Invoca email_search_tool
   ↓
FAISS: Retorna emails com palavras-chave relevantes
   ↓
Agente: Analisa sentimento e contexto
   ↓
Resposta: Conclusão baseada nos emails encontrados
```

#### 📘 Nível 3: Auditoria Contextual (Multi-Hop)
```
Usuário: "Verifique se houve desvio combinado nos emails"
   ↓
Agente: [Thought] "Preciso ver se combinaram algo"
   ↓
[Action 1] email_search_tool → "desvio fraude combinado"
   ↓
[Observation 1] "Email: vamos passar nota de $500"
   ↓
Agente: [Thought] "Encontrei $500, vou buscar no CSV"
   ↓
[Action 2] csv_analysis_tool → "transação de $500"
   ↓
[Observation 2] "TX_1234: Michael - $500 - Restaurante"
   ↓
Agente: [Final Answer] "Fraude confirmada! Email + Transação"
```

## 🚀 Como Executar

### 1. Pré-requisitos

- Python 3.10+
- Conta Google AI (para API key do Gemini)
- Git

### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/Gustavo-daCosta/Auditory-Chatbot.git
cd Auditory-Chatbot

# Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração da API Key

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione sua chave
# GOOGLE_API_KEY=sua_chave_aqui
```

**Como obter a API key**:
1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Crie uma nova API key
4. Cole no arquivo `.env`

### 4. Ingestão de Dados

```bash
# Execute APENAS UMA VEZ para carregar os dados no FAISS
python src/ingest_data.py
```

**Output esperado**:
```
🚀 Iniciando processo de ingestão de dados...
📄 Carregando política de compliance...
✂️  Documento dividido em 45 chunks
✅ Índice 'compliance' criado com sucesso!
📧 Carregando emails...
✂️  Documento dividido em 125 chunks
✅ Índice 'emails' criado com sucesso!
✨ Processo de ingestão concluído!
```

### 5. Executar o Chatbot

```bash
python src/main.py
```

**Interface**:
```
╔══════════════════════════════════════════════════════════════╗
║         🏢 CHATBOT DE AUDITORIA - DUNDER MIFFLIN 🏢          ║
╚══════════════════════════════════════════════════════════════╝

🔍 Digite sua pergunta (ou 'help' para ajuda):
```

### 6. Comandos Disponíveis

- `help` - Exibe menu de ajuda com exemplos
- `demo` - Executa demonstração dos 3 níveis
- `clear` - Limpa a tela
- `sair`/`exit` - Encerra o programa

## 📝 Exemplos de Uso

### Nível 1: Compliance
```
🔍 Posso gastar 200 dólares em um jantar com cliente?

💡 Não pode. A política de compliance da Dunder Mifflin limita 
refeições com clientes a $150. Conforme SEÇÃO 2.1...
```

### Nível 2: Investigação
```
🔍 O Michael Scott está conspirando contra o Toby?

💡 Sim, foram encontradas evidências nos emails. Michael enviou
mensagem para Dwight dizendo "Precisamos encontrar uma forma 
de transferir o Toby para a Costa Rica"...
```

### Nível 3: Auditoria Contextual
```
🔍 Verifique transações suspeitas acima de $500

💡 Foram identificadas 3 fraudes:
1. TX_1234 - Michael Scott - $680 em "Almoço" (limite: $150)
2. TX_5678 - Andy Bernard - $520 combinado em email...
```

## 🧪 Testes dos 3 Níveis

Execute o modo demo para ver o agente em ação:

```bash
python src/main.py
# Digite: demo
```

Ou teste individualmente cada nível com perguntas específicas.

## 📦 Estrutura do Projeto

```
Auditory-Chatbot/
├── README.md                    # Este arquivo
├── ARQUITETURA_AGENTES.md       # 🆕 Documentação da arquitetura multi-agente
├── requirements.txt             # Dependências Python
├── .env.example                 # Template de variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo Git
├── data/
│   ├── politica_compliance.txt  # Regras de compliance
│   ├── emails.txt               # Dump de emails internos
│   └── transacoes_bancarias.csv # Extrato de gastos
├── src/
│   ├── agents/                  # 🆕 Pasta de agentes especializados
│   │   ├── __init__.py          # Exports dos agentes
│   │   ├── orchestrator_agent.py # 🎯 Agente Orquestrador (coordenador)
│   │   ├── policy_agent.py      # 📋 Policy Agent (regras/compliance)
│   │   ├── conspiracy_agent.py  # 🕵️ Conspiracy Agent (emails/investigação)
│   │   └── compliance_agent.py  # 💰 Compliance Agent (transações/auditoria)
│   ├── ingest_data.py           # Módulo de ingestão
│   ├── tools.py                 # [DEPRECATED] Mantido para compatibilidade
│   └── main.py                  # Interface principal (usa OrchestratorAgent)
└── faiss_index/                 # Índices vetoriais (gerado)
    ├── compliance/              # Índice de políticas
    └── emails/                  # Índice de emails
```

## 🔧 Tecnologias Utilizadas

- **LangChain 0.3.18**: Framework de orquestração de LLMs
- **Google Gemini 2.0 Flash Exp**: Modelo de linguagem
- **FAISS 1.9**: Banco de dados vetorial (Facebook AI Similarity Search)
- **Pandas 2.2.3**: Análise de dados estruturados
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

## 🎯 Decisões de Design

### Por que LangChain?
- Abstração robusta para agentes orquestradores
- Sistema de tools maduro e extensível
- Integração nativa com FAISS e Gemini

### Por que FAISS?
- Extremamente rápido e eficiente
- Sem dependências pesadas (leve)
- Desenvolvido pelo Facebook AI Research
- Ideal para busca de similaridade em larga escala

### Por que Gemini 2.0?
- API gratuita e generosa
- Performance excelente (Flash Exp)
- Suporte nativo no LangChain

### Por que ReAct e não RAG simples?
- RAG simples não resolve Nível 3 (multi-hop)
- ReAct permite raciocínio em múltiplos passos
- Transparência no processo de decisão

## 🐛 Troubleshooting

### Erro: "GOOGLE_API_KEY não configurada"
**Solução**: Configure o arquivo `.env` com sua chave

### Erro: "Index not found"
**Solução**: Execute `python src/ingest_data.py` primeiro

### Erro: "Module not found"
**Solução**: Ative o ambiente virtual e reinstale dependências

### Ingestão com problemas
**Solução**: Delete a pasta `faiss_index` e reingira os dados

## 📹 Vídeo de Demonstração

[Link para o vídeo será adicionado aqui]

## 👨‍💻 Autor

**Gustavo da Costa**
- GitHub: [@Gustavo-daCosta](https://github.com/Gustavo-daCosta)

## 📄 Licença

Este projeto foi desenvolvido como atividade acadêmica.

---

**Nota**: Este sistema é um protótipo educacional. Em produção, seria necessário:
- Autenticação e autorização
- Logging estruturado
- Testes automatizados
- Interface web (Streamlit/Gradio)
- Rate limiting da API
- Backup dos índices FAISS
