from pulp import *
import pandas as pd

def calcular_racao_minima(alimentos, nutrientes_requeridos, peso_total_racao=20):
    """
    Calcula a composição de ração de custo mínimo usando programação linear.
    
    Args:
        alimentos: DataFrame com colunas [nome, preco, ms, pB, ndt, ca, p]
        nutrientes_requeridos: Dict com requisitos mínimos de cada nutriente
        peso_total_racao: Quantidade total de ração diária em kg
    
    Returns:
        DataFrame com a quantidade de cada alimento na ração final
    """
    # Criar o problema de minimização
    prob = LpProblem("Racao_Vaca_Leiteira", LpMinimize)
    
    # Criar variáveis de decisão (quantidade de cada alimento)
    variaveis = {}
    for nome in alimentos['nome']:
        variaveis[nome] = LpVariable(nome, 0, None)
    
    # Função objetivo: minimizar custo total
    prob += lpSum([variaveis[nome] * alimentos.loc[alimentos['nome']==nome, 'preco'].values[0] 
                   for nome in alimentos['nome']])
    
    # Restrição de peso total
    prob += lpSum([variaveis[nome] for nome in alimentos['nome']]) == peso_total_racao
    
    # Restrições de nutrientes mínimos
    # Proteína Bruta (PB)
    prob += lpSum([variaveis[nome] * alimentos.loc[alimentos['nome']==nome, 'pB'].values[0] 
                   for nome in alimentos['nome']]) >= nutrientes_requeridos['pB'] * peso_total_racao
    
    # Nutrientes Digestíveis Totais (NDT)
    prob += lpSum([variaveis[nome] * alimentos.loc[alimentos['nome']==nome, 'ndt'].values[0] 
                   for nome in alimentos['nome']]) >= nutrientes_requeridos['ndt'] * peso_total_racao
    
    # Cálcio (Ca)
    prob += lpSum([variaveis[nome] * alimentos.loc[alimentos['nome']==nome, 'ca'].values[0] 
                   for nome in alimentos['nome']]) >= nutrientes_requeridos['ca'] * peso_total_racao
    
    # Fósforo (P)
    prob += lpSum([variaveis[nome] * alimentos.loc[alimentos['nome']==nome, 'p'].values[0] 
                   for nome in alimentos['nome']]) >= nutrientes_requeridos['p'] * peso_total_racao
    
    # Matéria Seca mínima
    prob += lpSum([variaveis[nome] * alimentos.loc[alimentos['nome']==nome, 'ms'].values[0] 
                   for nome in alimentos['nome']]) >= nutrientes_requeridos['ms'] * peso_total_racao
    
    # Resolver o problema
    prob.solve()
    
    # Preparar resultados
    resultados = []
    for nome in alimentos['nome']:
        quantidade = value(variaveis[nome])
        if quantidade > 0.001:  # Filtrar quantidades muito pequenas
            custo = quantidade * alimentos.loc[alimentos['nome']==nome, 'preco'].values[0]
            resultados.append({
                'alimento': nome,
                'quantidade_kg': round(quantidade, 2),
                'custo': round(custo, 2)
            })
    
    return pd.DataFrame(resultados)

# Dados dos alimentos para vaca leiteira
# Valores nutricionais baseados em tabelas de composição de alimentos para bovinos
dados_alimentos = {
    'nome': [
        'Silagem de Milho',
        'Feno de Tifton',
        'Farelo de Soja',
        'Milho Moído',
        'Caroço de Algodão',
        'Minerais'
    ],
    'preco': [
        0.80,   # Silagem de Milho (R$/kg)
        1.20,   # Feno de Tifton
        3.50,   # Farelo de Soja
        2.00,   # Milho Moído
        2.50,   # Caroço de Algodão
        4.00    # Minerais
    ],
    'ms': [    # Matéria Seca (%)
        35.0,   # Silagem de Milho
        85.0,   # Feno de Tifton
        88.0,   # Farelo de Soja
        88.0,   # Milho Moído
        90.0,   # Caroço de Algodão
        98.0    # Minerais
    ],
    'pB': [    # Proteína Bruta (%)
        7.5,    # Silagem de Milho
        12.0,   # Feno de Tifton
        45.0,   # Farelo de Soja
        9.0,    # Milho Moído
        23.0,   # Caroço de Algodão
        0.0     # Minerais
    ],
    'ndt': [   # Nutrientes Digestíveis Totais (%)
        65.0,   # Silagem de Milho
        55.0,   # Feno de Tifton
        80.0,   # Farelo de Soja
        85.0,   # Milho Moído
        80.0,   # Caroço de Algodão
        0.0     # Minerais
    ],
    'ca': [    # Cálcio (%)
        0.30,   # Silagem de Milho
        0.45,   # Feno de Tifton
        0.30,   # Farelo de Soja
        0.03,   # Milho Moído
        0.20,   # Caroço de Algodão
        16.0    # Minerais
    ],
    'p': [     # Fósforo (%)
        0.22,   # Silagem de Milho
        0.20,   # Feno de Tifton
        0.65,   # Farelo de Soja
        0.25,   # Milho Moído
        0.60,   # Caroço de Algodão
        8.0     # Minerais
    ]
}

alimentos_df = pd.DataFrame(dados_alimentos)

# Requisitos nutricionais diários para uma vaca leiteira
# Valores baseados em recomendações do NRC para uma vaca de 600kg produzindo 25L de leite/dia
requisitos = {
    'ms': 0.40,     # Mínimo 40% de Matéria Seca
    'pB': 0.16,     # Mínimo 16% de Proteína Bruta
    'ndt': 0.68,    # Mínimo 68% de NDT
    'ca': 0.006,    # Mínimo 0.6% de Cálcio
    'p': 0.004      # Mínimo 0.4% de Fósforo
}

# Calcular a ração (20kg de ração/dia)
resultado = calcular_racao_minima(alimentos_df, requisitos, peso_total_racao=20)

# Exibir resultados
print("\nComposição da Ração Diária para Vaca Leiteira:")
print(resultado)

# Calcular custo total
custo_total = resultado['custo'].sum()
print(f"\nCusto Total da Ração Diária: R$ {custo_total:.2f}")