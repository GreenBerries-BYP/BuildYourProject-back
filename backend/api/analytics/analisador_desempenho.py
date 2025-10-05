from django.utils import timezone
from ..utils.metricas_projeto import calcular_metricas_projeto

class AnalisadorDesempenho:
    """
    SISTEMA DE ANÁLISE DE DESEMPENHO BASEADO EM EARNED VALUE MANAGEMENT
    """
    
    def __init__(self):
        pass
    
    def analisar_situacao_projeto(self, projeto):
        """
        Analisa a situação atual do projeto baseado em múltiplas métricas EVM
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
        
        # ✅ LÓGICA CONSISTENTE ENTRE SPI E STATUS
        if spi >= 1.1:
            status = "ADIANTADO"
            cor = "verde"
            explicacao = "Projeto adiantado em relação ao cronograma"
        elif spi >= 0.95:
            status = "NO PRAZO" 
            cor = "verde-claro"
            explicacao = "Projeto dentro do cronograma planejado"
        elif spi >= 0.85:
            status = "ATENÇÃO"
            cor = "amarelo" 
            explicacao = "Projeto com pequeno desvio do cronograma"
        elif spi >= 0.7:
            status = "ATRASO MODERADO"
            cor = "laranja"
            explicacao = "Projeto com atraso moderado"
        else:
            status = "ATRASO CRÍTICO"
            cor = "vermelho"
            explicacao = "Projeto com atraso crítico"
        
        # ✅ CALCULAR TAREFAS PENDENTES
        tarefas_pendentes = metricas['total_tarefas'] - metricas['tarefas_concluidas']
        
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
            'tarefas_pendentes': tarefas_pendentes,  
            'taxa_conclusao': metricas['taxa_conclusao'],
            'total_tarefas': metricas['total_tarefas'],
            'tarefas_concluidas': metricas['tarefas_concluidas']
        }
