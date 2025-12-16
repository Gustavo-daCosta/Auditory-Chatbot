"""
Conspiracy Agent - Agente especializado em investigação de emails
Responsável por detectar conversas suspeitas e conspirações
"""
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool


class ConspiracyAgent:
    """Agente especializado em investigação de emails e comunicações internas"""
    
    def __init__(self, persist_directory: str = "./faiss_index"):
        """
        Inicializa o Conspiracy Agent
        
        Args:
            persist_directory: Diretório onde os índices FAISS estão salvos
        """
        self.persist_directory = persist_directory
        
        # Inicializa embeddings locais
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.tool = self._create_email_tool()
    
    def _create_email_tool(self):
        """Cria a ferramenta de busca nos emails"""
        try:
            # Carrega o índice FAISS
            emails_path = os.path.join(self.persist_directory, "emails")
            vectorstore = FAISS.load_local(
                emails_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Cria o retriever
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 7}
            )
            
            # Cria a tool usando create_retriever_tool
            email_tool = create_retriever_tool(
                retriever=retriever,
                name="email_search",
                description=(
                    "Busca informações nos EMAILS INTERNOS da empresa. "
                    "Use esta ferramenta para investigar CONVERSAS, CONSPIRAÇÕES, PLANOS, "
                    "COMBINAÇÕES entre funcionários ou qualquer comunicação suspeita. "
                    "Exemplos de uso: 'Michael está tramando contra Toby?', "
                    "'Alguém combinou desvio de verba?', 'O que fulano disse sobre X?'"
                )
            )
            
            return email_tool
            
        except Exception as e:
            print(f"Erro ao criar Conspiracy Agent: {e}")
            raise
    
    def get_tool(self):
        """Retorna a ferramenta do agente"""
        return self.tool
