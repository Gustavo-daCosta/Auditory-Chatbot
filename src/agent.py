"""
Agente de Auditoria ReAct (Reason + Act)
Orquestra as ferramentas para responder perguntas investigativas
"""
import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

from tools import AuditoryTools

load_dotenv()

class AuditoryAgent:
    """Agente de auditoria inteligente para a Dunder Mifflin"""
    
    def __init__(self, verbose: bool = True):
        """
        Inicializa o agente de auditoria
        
        Args:
            verbose: Se True, exibe o raciocínio do agente
        """
        self.verbose = verbose
        
        # Verifica API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError("GOOGLE_API_KEY não configurada. ")
        
        # Inicializa o LLM (Gemini)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0,
            google_api_key=api_key
        )
        
        # Carrega as ferramentas
        print("🔧 Inicializando ferramentas...")
        tools_manager = AuditoryTools()
        self.tools = tools_manager.get_tools()
        
        # Cria o agente ReAct
        self.agent = self._create_react_agent()
        
        print("✅ Agente de auditoria inicializado!\n")
    
    def _create_react_agent(self) -> AgentExecutor:
        """
        Cria o agente ReAct com o prompt personalizado
        
        Returns:
            Agente executor configurado
        """
        # Template de prompt para o agente ReAct
        react_prompt = PromptTemplate.from_template("""
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

INSTRUÇÕES DE RACIOCÍNIO (ReAct):
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
            prompt=react_prompt
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
        Faz uma pergunta ao agente
        
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
    """Função principal"""
    print("🚀 Inicializando Agente de Auditoria da Dunder Mifflin...\n")
    
    try:
        agent = AuditoryAgent(verbose=True)
        
        print("Agente pronto! Digite 'sair' para encerrar.\n")
        
        while True:
            pergunta = input("🔍 Sua pergunta: ").strip()
            
            if pergunta.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Encerrando agente. Até logo!")
                break
            
            if not pergunta:
                continue
            
            print()
            resposta = agent.query(pergunta)
            print(f"\n💡 Resposta:\n{resposta}\n")
            print("-" * 80 + "\n")
    
    except Exception as e:
        print(f"❌ Erro fatal: {e}")


if __name__ == "__main__":
    main()
