"""
Interface Principal do Chatbot de Auditoria
Sistema de linha de comando para interagir com o agente
"""
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import AuditoryAgent


def print_banner():
    """Exibe o banner do sistema"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                  🏢 CHATBOT DE AUDITORIA - DUNDER MIFFLIN 🏢                  ║
║                                                                              ║
║                        Sistema de Auditoria Inteligente                      ║
║                     Desenvolvido por ordem de Toby Flenderson                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """Exibe o menu de ajuda"""
    help_text = """
📋 COMANDOS DISPONÍVEIS:

  help       - Exibe este menu de ajuda
  clear      - Limpa a tela
  sair/exit  - Encerra o programa

📊 EXEMPLOS DE PERGUNTAS:

  Nível 1 - Compliance:
    • Posso gastar 200 dólares em um jantar?
    • Qual o limite para despesas intermediárias?
    • Quem pode aprovar gastos acima de $500?
  
  Nível 2 - Investigação de Emails:
    • O Michael está conspirando contra o Toby?
    • Alguém está planejando algo suspeito nos emails?
    • O que o Dwight disse sobre fraudes?
  
  Nível 3 - Auditoria Contextual:
    • Verifique transações suspeitas acima de $500
    • Existe alguma fraude combinada nos emails?
    • Quais gastos do Michael violam as regras?

"""
    print(help_text)


def clear_screen():
    """Limpa a tela do terminal"""
    os.system('clear' if os.name != 'nt' else 'cls')


def main():
    """Função principal"""
    clear_screen()
    print_banner()
    
    print("🔄 Inicializando o sistema...")
    print("   (Isso pode levar alguns segundos...)\n")
    
    try:
        # Inicializa o agente
        agent = AuditoryAgent(verbose=False)
        
        print("✅ Sistema inicializado com sucesso!\n")
        print_help()
        
        # Loop principal
        while True:
            try:
                # Prompt para o usuário
                pergunta = input("\n🔍 Digite sua pergunta (ou 'help' para ajuda): ").strip()
                
                # Comandos especiais
                if not pergunta:
                    continue
                
                if pergunta.lower() in ['sair', 'exit', 'quit', 'q']:
                    print("\n👋 Encerrando o sistema. Até logo!")
                    break
                
                if pergunta.lower() == 'help':
                    print_help()
                    continue
                
                if pergunta.lower() == 'clear':
                    clear_screen()
                    print_banner()
                    continue
                
                # Processa a pergunta
                print("\n⏳ Analisando... (O agente está pensando)\n")
                resposta = agent.query(pergunta)
                
                print("=" * 80)
                print("💡 RESPOSTA:")
                print("=" * 80)
                print(f"\n{resposta}\n")
                print("=" * 80)
                
            except KeyboardInterrupt:
                print("\n\n👋 Operação cancelada. Encerrando...")
                break
            except Exception as e:
                print(f"\n❌ Erro ao processar pergunta: {e}")
                print("   Tente novamente ou digite 'help' para ajuda.\n")
    
    except FileNotFoundError as e:
        print(f"\n❌ ERRO: {e}")
        print("\n💡 SOLUÇÃO:")
        print("   Execute primeiro: python src/ingest_data.py")
        print("   Isso irá carregar os dados no ChromaDB.\n")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n❌ ERRO: {e}")
        print("\n💡 SOLUÇÃO:")
        print("   1. Copie o arquivo .env.example para .env")
        print("   2. Adicione sua GOOGLE_API_KEY no arquivo .env")
        print("   3. Execute novamente\n")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

