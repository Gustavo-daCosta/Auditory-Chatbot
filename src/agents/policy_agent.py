"""
Policy Agent - Agente especializado em políticas de compliance
Responsável por consultar e interpretar regras corporativas
"""
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool


class PolicyAgent:
    """Agente especializado em políticas e regras de compliance"""
    
    def __init__(self, persist_directory: str = "./faiss_index"):
        """
        Inicializa o Policy Agent
        
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
        
        self.tool = self._create_policy_tool()
    
    def _create_policy_tool(self):
        """Cria a ferramenta de busca na política de compliance"""
        try:
            # Carrega o índice FAISS
            compliance_path = os.path.join(self.persist_directory, "compliance")
            vectorstore = FAISS.load_local(
                compliance_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Cria o retriever
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # Cria a tool usando create_retriever_tool
            policy_tool = create_retriever_tool(
                retriever=retriever,
                name="policy_retriever",
                description=(
                    "Busca informações na POLÍTICA DE COMPLIANCE da Dunder Mifflin. "
                    "Use esta ferramenta quando precisar consultar REGRAS, LIMITES DE GASTOS, "
                    "ALÇADAS DE APROVAÇÃO, CATEGORIAS PERMITIDAS ou qualquer norma corporativa. "
                    "Exemplos de uso: 'Qual o limite para refeições?', 'Posso gastar X reais?', "
                    "'Quem aprova despesas acima de $500?'"
                )
            )
            
            return policy_tool
            
        except Exception as e:
            print(f"Erro ao criar Policy Agent: {e}")
            raise
    
    def get_tool(self):
        """Retorna a ferramenta do agente"""
        return self.tool
