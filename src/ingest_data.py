"""
Módulo de Ingestão de Dados para FAISS
Carrega documentos (compliance e emails) em índices separados
"""
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

class DataIngestion:
    """Classe para gerenciar a ingestão de dados no FAISS"""
    
    def __init__(self, persist_directory: str = "./faiss_index"):
        """
        Inicializa o sistema de ingestão
        
        Args:
            persist_directory: Diretório onde os índices FAISS serão salvos
        """
        self.persist_directory = persist_directory
        
        # Inicializa o modelo de embeddings local
        print("Carregando modelo de embeddings local...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
    def ingest_compliance_policy(self, file_path: str) -> FAISS:
        """
        Ingere a política de compliance no FAISS
        
        Args:
            file_path: Caminho para o arquivo politica_compliance.txt
            
        Returns:
            Instância do FAISS vectorstore
        """
        
        # Carrega o documento
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        
        # Divide em chunks menores para precisão nas regras
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        
        compliance_path = os.path.join(self.persist_directory, "compliance")
        vectorstore.save_local(compliance_path)
        
        print(f"✅ Índice 'compliance' criado com sucesso!")
        return vectorstore
    
    def ingest_emails(self, file_path: str) -> FAISS:
        """
        Ingere os emails no FAISS
        
        Args:
            file_path: Caminho para o arquivo emails.txt
            
        Returns:
            Instância do FAISS vectorstore
        """
        # Carrega o documento
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        
        # Divide em chunks maiores para manter contexto das conversas
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n-------------------------------------------------------------------------------\n", "\n\n", "\n", " "]
        )
        chunks = text_splitter.split_documents(documents)
        
        # Cria o índice FAISS
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        
        # Salva o índice
        emails_path = os.path.join(self.persist_directory, "emails")
        vectorstore.save_local(emails_path)

        return vectorstore
    
    def check_if_ingested(self) -> bool:
        """
        Verifica se os dados já foram ingeridos
        
        Returns:
            True se já existem índices, False caso contrário
        """
        if not os.path.exists(self.persist_directory):
            return False
        
        compliance_path = os.path.join(self.persist_directory, "compliance")
        return os.path.exists(compliance_path)


def main():
    """Função principal para executar a ingestão"""
    print("Iniciando processo de ingestão de dados...\n")
    
    # Inicializa o sistema de ingestão
    ingestion = DataIngestion()
    
    # Verifica se já foi ingerido
    if ingestion.check_if_ingested():
        print("Dados já foram ingeridos anteriormente.")
        print("Para reingerir, delete a pasta 'faiss_index' e execute novamente.")
        return
    
    # Define os caminhos dos arquivos
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    compliance_path = os.path.join(base_dir, "data", "politica_compliance.txt")
    emails_path = os.path.join(base_dir, "data", "emails.txt")
    
    # Verifica se os arquivos existem
    if not os.path.exists(compliance_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {compliance_path}")
    if not os.path.exists(emails_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {emails_path}")
    
    # Ingere os documentos
    ingestion.ingest_compliance_policy(compliance_path)
    print()
    ingestion.ingest_emails(emails_path)
    
    print("\nProcesso de ingestão concluído com sucesso!")

if __name__ == "__main__":
    main()
