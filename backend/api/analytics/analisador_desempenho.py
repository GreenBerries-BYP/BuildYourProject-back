from django.utils import timezone
from ..utils.metricas_projeto import calcular_metricas_projeto

class AnalisadorDesempenho:
    """
    SISTEMA DE ANÁLISE DE DESEMPENHO CORRIGIDO E CONSISTENTE
    """
    
    def __init__(self):
        pass
    
    def analisar_situacao_projeto(self, projeto):
        """
        Analisa a situação atual do projeto baseado em múltiplas métricas
        """
        metricas = calcular_metricas_projeto(projeto.id)
        if not metricas:
            return {'erro': 'Não foi possível calcular métricas'}
            
        # ✅ VERIFICAR SE PROJETO ESTÁ FINALIZADO
        if metricas['taxa_conclusao'] >= 99.9:
            return {
                'status': "CONCLUÍDO",
                'cor': "verde",
                'explicacao': "🎉 Projeto finalizado com sucesso! Parabéns pela conclusão!",
                'spi': 1.0,
                'sv': 0,
                'tcpi': 1.0,
                'eac': metricas['total_dias'],
                'vac': 0,
                'dias_restantes': 0,
                'tarefas_atrasadas': 0,
                'tarefas_pendentes': 0, 
                'taxa_conclusao': 100,
                'total_tarefas': metricas['total_tarefas'],
                'tarefas_concluidas': metricas['tarefas_concluidas']
            }
        
        spi = metricas['spi']
        tarefas_atrasadas = metricas['tarefas_atrasadas']
        projeto_atrasado = metricas['projeto_atrasado']
        taxa_conclusao = metricas['taxa_conclusao']
        
        # ✅ LÓGICA CONSISTENTE: Projeto atrasado SEMPRE tem status crítico
        if projeto_atrasado and metricas['tarefas_pendentes'] > 0:
            status = "ATRASO CRÍTICO"
            cor = "vermelho"
            explicacao = f"⚠️ PROJETO ATRASADO! {metricas['tarefas_pendentes']} tarefas pendentes após o prazo final"
        
        # ✅ LÓGICA BASEADA EM SPI E TAREFAS ATRASADAS
        elif spi >= 1.1 and tarefas_atrasadas == 0:
            status = "ADIANTADO"
            cor = "verde"
            explicacao = "Projeto adiantado em relação ao cronograma"
        elif spi >= 0.95 and tarefas_atrasadas == 0:
            status = "NO PRAZO" 
            cor = "verde-claro"
            explicacao = "Projeto dentro do cronograma planejado"
        elif spi >= 0.85 or tarefas_atrasadas <= 2:
            status = "ATENÇÃO"
            cor = "amarelo" 
            explicacao = f"Projeto com pequeno desvio - {tarefas_atrasadas} tarefas atrasadas"
        elif spi >= 0.6 or tarefas_atrasadas <= 5:
            status = "ATRASO MODERADO"
            cor = "laranja"
            explicacao = f"Projeto com atraso moderado - {tarefas_atrasadas} tarefas atrasadas"
        else:
            status = "ATRASO CRÍTICO"
            cor = "vermelho"
            explicacao = f"Projeto com atraso crítico - {tarefas_atrasadas} tarefas atrasadas"
        
        return {
            'status': status,
            'cor': cor,
            'explicacao': explicacao,
            'spi': round(spi, 3),
            'sv': metricas['sv'],
            'tcpi': metricas['tcpi'],
            'eac': metricas['eac'],
            'vac': metricas['vac'],
            'dias_restantes': metricas['dias_restantes'],
            'tarefas_atrasadas': metricas['tarefas_atrasadas'],
            'tarefas_pendentes': metricas['tarefas_pendentes'],  
            'taxa_conclusao': metricas['taxa_conclusao'],
            'total_tarefas': metricas['total_tarefas'],
            'tarefas_concluidas': metricas['tarefas_concluidas']
        }
