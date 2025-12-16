"""
Compliance Agent - Agente especializado em análise de transações
Responsável por auditar gastos e identificar irregularidades
"""
import os
import pandas as pd
from langchain.tools import Tool


class ComplianceAgent:
    """Agente especializado em análise de transações e auditoria de gastos"""
    
    def __init__(self):
        """Inicializa o Compliance Agent"""
        # Carrega o CSV de transações
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(base_dir, "data", "transacoes_bancarias.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV não encontrado: {csv_path}")
        
        self.df_transactions = pd.read_csv(csv_path)
        self.tool = self.analysis_tool()
    
    def analysis_tool(self):
        """Cria a ferramenta de análise do CSV de transações"""
        
        def analyze_transactions(query: str) -> str:
            """
            Analisa transações bancárias baseado em uma query
            
            Args:
                query: Descrição da análise desejada
                
            Returns:
                Resultado da análise em texto
            """
            query_lower = query.lower()
            
            try:
                # Análise 1: Buscar transações acima de um valor
                if "acima" in query_lower or "maior" in query_lower or "mais de" in query_lower:
                    # Extrai o valor da query
                    import re
                    valor_match = re.search(r'\$?\s*(\d+(?:\.\d+)?)', query)
                    if valor_match:
                        valor_limite = float(valor_match.group(1))
                        resultado = self.df_transactions[self.df_transactions['valor'] > valor_limite]
                        
                        if len(resultado) == 0:
                            return f"Nenhuma transação encontrada acima de ${valor_limite}."
                        
                        # Formata o resultado
                        output = f"Encontradas {len(resultado)} transações acima de ${valor_limite}:\n\n"
                        for _, row in resultado.head(20).iterrows():
                            output += f"- {row['id_transacao']}: {row['funcionario']} - ${row['valor']:.2f} - {row['descricao']}\n"
                        
                        if len(resultado) > 20:
                            output += f"\n... e mais {len(resultado) - 20} transações."
                        
                        return output
                
                # Análise 2: Buscar por funcionário
                elif "funcionario" in query_lower or any(nome in query_lower for nome in ['michael', 'dwight', 'jim', 'pam', 'toby', 'angela', 'kevin', 'oscar', 'stanley', 'phyllis', 'andy', 'meredith', 'creed', 'darryl', 'ryan', 'kelly']):
                    # Extrai o nome do funcionário
                    for nome in ['michael scott', 'dwight schrute', 'jim halpert', 'pam beesly', 'toby flenderson', 'angela martin', 'kevin malone', 'oscar martinez', 'stanley hudson', 'phyllis vance', 'andy bernard', 'meredith palmer', 'creed bratton', 'darryl philbin', 'ryan howard', 'kelly kapoor']:
                        if nome.split()[0] in query_lower:
                            resultado = self.df_transactions[
                                self.df_transactions['funcionario'].str.lower().str.contains(nome.split()[0])
                            ]
                            
                            if len(resultado) == 0:
                                return f"Nenhuma transação encontrada para {nome.title()}."
                            
                            # Calcula estatísticas
                            total = resultado['valor'].sum()
                            media = resultado['valor'].mean()
                            max_transacao = resultado.loc[resultado['valor'].idxmax()]
                            
                            output = f"Análise de transações de {resultado.iloc[0]['funcionario']}:\n\n"
                            output += f"Total de transações: {len(resultado)}\n"
                            output += f"Valor total: ${total:.2f}\n"
                            output += f"Valor médio: ${media:.2f}\n"
                            output += f"Maior transação: ${max_transacao['valor']:.2f} - {max_transacao['descricao']}\n\n"
                            output += "Últimas 10 transações:\n"
                            
                            for _, row in resultado.tail(10).iterrows():
                                output += f"- {row['data']}: ${row['valor']:.2f} - {row['descricao']}\n"
                            
                            return output
                
                # Análise 3: Buscar por categoria
                elif "categoria" in query_lower or "tipo" in query_lower:
                    categorias = self.df_transactions.groupby('categoria').agg({
                        'valor': ['sum', 'count', 'mean']
                    }).round(2)
                    
                    output = "Resumo por categoria:\n\n"
                    for categoria, row in categorias.iterrows():
                        output += f"- {categoria}:\n"
                        output += f"  Total: ${row[('valor', 'sum')]:.2f}\n"
                        output += f"  Quantidade: {int(row[('valor', 'count')])} transações\n"
                        output += f"  Média: ${row[('valor', 'mean')]:.2f}\n\n"
                    
                    return output
                
                # Análise 4: Buscar transações específicas por valor exato
                elif "exatamente" in query_lower or "valor de" in query_lower:
                    import re
                    valor_match = re.search(r'\$?\s*(\d+(?:\.\d+)?)', query)
                    if valor_match:
                        valor_exato = float(valor_match.group(1))
                        resultado = self.df_transactions[self.df_transactions['valor'] == valor_exato]
                        
                        if len(resultado) == 0:
                            # Tenta buscar valores aproximados (± 1)
                            resultado = self.df_transactions[
                                (self.df_transactions['valor'] >= valor_exato - 1) & 
                                (self.df_transactions['valor'] <= valor_exato + 1)
                            ]
                        
                        if len(resultado) == 0:
                            return f"Nenhuma transação encontrada com valor ${valor_exato}."
                        
                        output = f"Transações encontradas com valor ${valor_exato}:\n\n"
                        for _, row in resultado.iterrows():
                            output += f"- {row['id_transacao']} ({row['data']}): {row['funcionario']} - ${row['valor']:.2f}\n"
                            output += f"  Descrição: {row['descricao']}\n"
                            output += f"  Categoria: {row['categoria']}\n\n"
                        
                        return output
                
                # Análise 5: Resumo geral
                else:
                    total_transacoes = len(self.df_transactions)
                    valor_total = self.df_transactions['valor'].sum()
                    valor_medio = self.df_transactions['valor'].mean()
                    maior_gasto = self.df_transactions.loc[self.df_transactions['valor'].idxmax()]
                    
                    output = f"Resumo geral das transações:\n\n"
                    output += f"Total de transações: {total_transacoes}\n"
                    output += f"Valor total: ${valor_total:.2f}\n"
                    output += f"Valor médio por transação: ${valor_medio:.2f}\n"
                    output += f"Maior gasto: ${maior_gasto['valor']:.2f} por {maior_gasto['funcionario']}\n"
                    output += f"  ({maior_gasto['descricao']})\n\n"
                    output += f"Colunas disponíveis: {', '.join(self.df_transactions.columns)}\n"
                    
                    return output
                    
            except Exception as e:
                return f"Erro ao analisar transações: {str(e)}\nQuery recebida: {query}"
        
        # Cria a tool
        csv_tool = Tool(
            name="csv_analysis",
            func=analyze_transactions,
            description=(
                "Analisa a PLANILHA DE TRANSAÇÕES BANCÁRIAS (CSV) dos funcionários. "
                "Use esta ferramenta para BUSCAR GASTOS, VERIFICAR VALORES, SOMAR DESPESAS, "
                "FILTRAR por funcionário, categoria ou valor, e IDENTIFICAR FRAUDES. "
                "Você pode pedir: 'transações acima de $500', 'gastos do Michael', "
                "'resumo por categoria', 'transação de valor exatamente $X'. "
                "A ferramenta tem acesso a: id_transacao, data, funcionario, cargo, "
                "descricao, valor, categoria, departamento."
            )
        )
        
        return csv_tool
    
    def get_tool(self):
        """Retorna a ferramenta do agente"""
        return self.tool
