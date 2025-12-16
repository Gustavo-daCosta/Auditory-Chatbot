"""
Orchestrator Agent - Agente orquestrador principal
Coordena os agentes especializados (Policy, Conspiracy, Compliance)
"""
import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

from .policy_agent import PolicyAgent
from .conspiracy_agent import ConspiracyAgent
from .compliance_agent import ComplianceAgent

load_dotenv()


class OrchestratorAgent:
    """Agente orquestrador que coordena os agentes especializados"""
    
    def __init__(self, verbose: bool = True):
        """
        Inicializa o agente orquestrador
        
        Args:
            verbose: Se True, exibe o raciocínio do agente
        """
        self.verbose = verbose
        
        # Verifica API key
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Inicializa o LLM (Gemini)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0,
            google_api_key=api_key
        )
        
        # Inicializa os agentes especializados
        self.policy_agent = PolicyAgent()
        self.conspiracy_agent = ConspiracyAgent()
        self.compliance_agent = ComplianceAgent()
        
        # Coleta as ferramentas dos agentes
        self.tools = [
            self.policy_agent.get_tool(),
            self.conspiracy_agent.get_tool(),
            self.compliance_agent.get_tool()
        ]
        
        # Cria o agente orquestrador
        self.agent = self._create_orchestrator_agent()
        
        print("\nOrquestrador inicializado!\n")
    
    def _create_orchestrator_agent(self) -> AgentExecutor:
        """
        Cria o agente orquestrador com o prompt personalizado
        
        Returns:
            Agente executor configurado
        """
        # Template de prompt para o agente orquestrador
        orchestrator_prompt = PromptTemplate.from_template("""
Você é Toby Flenderson Jr., um AGENTE DE AUDITORIA ESPECIALIZADO da Dunder Mifflin.
Seu trabalho é investigar fraudes, verificar compliance e responder perguntas sobre 
gastos corporativos com PRECISÃO e EVIDÊNCIAS.

PERSONALIDADE:
- Meticuloso e detalhista (como Toby)
- Sempre cita fontes e evidências
- Não faz suposições - busca dados concretos
- Quando encontra uma fraude, explica EXATAMENTE por que é fraude

FERRAMENTAS DISPONÍVEIS:
{tools}

NOMES DAS FERRAMENTAS: {tool_names}

INSTRUÇÕES DE RACIOCÍNIO (ORQUESTRADOR):
Para cada pergunta, você deve seguir este ciclo:

Thought: Analise o que você precisa descobrir
Action: Escolha UMA ferramenta para usar
Action Input: O input para a ferramenta
Observation: O resultado da ferramenta
... (repita Thought/Action/Action Input/Observation quantas vezes necessário)
Thought: Agora eu sei a resposta final
Final Answer: A resposta completa com evidências

REGRAS IMPORTANTES:
1. SEMPRE use as ferramentas disponíveis - não invente informações
2. Para questões de compliance, use policy_retriever PRIMEIRO
3. Para investigar conversas/conspirações, use email_search
4. Para analisar gastos/transações, use csv_analysis
5. Para fraudes contextuais (Nível 3), você precisa:
   a) Buscar nos emails o que foi combinado
   b) Buscar no CSV se a transação realmente aconteceu
   c) Comparar e concluir
6. SEMPRE cite números de transação, valores e datas quando falar de gastos
7. SEMPRE cite trechos de emails ou regras quando apresentar evidências

FORMATO DE RESPOSTA:
Sua resposta final deve ter:
- Resposta clara e direta
- Evidências concretas (trechos de documentos, valores, IDs)
- Conclusão fundamentada

PERGUNTA DO USUÁRIO: {input}

HISTÓRICO DE PENSAMENTOS E AÇÕES:
{agent_scratchpad}
""")
        
        # Cria o agente
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=orchestrator_prompt
        )
        
        # Cria o executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="generate"
        )
        
        return agent_executor
    
    def query(self, question: str) -> str:
        """
        Faz uma pergunta ao agente orquestrador
        
        Args:
            question: Pergunta do usuário
            
        Returns:
            Resposta do agente
        """
        try:
            result = self.agent.invoke({"input": question})
            return result["output"]
        except Exception as e:
            return f"❌ Erro ao processar pergunta: {str(e)}"


def main():
    """Função principal para teste"""
    print("Inicializando Orquestrador de Auditoria da Dunder Mifflin...\n")
    
    try:
        orchestrator = OrchestratorAgent(verbose=True)
        
        print("Orquestrador pronto! Digite 'sair' para encerrar.\n")
        
        while True:
            pergunta = input("🔍 Sua pergunta: ").strip()
            
            if pergunta.lower() in ['sair', 'exit', 'quit']:
                print("\n Encerrando orquestrador. Até logo!")
                break
            
            if not pergunta:
                continue
            
            print()
            resposta = orchestrator.query(pergunta)
            print(f"\n Resposta:\n{resposta}\n")
            print("-" * 80 + "\n")
    
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()
