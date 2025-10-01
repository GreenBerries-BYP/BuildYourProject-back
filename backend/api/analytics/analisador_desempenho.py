from django.utils import timezone
from ..utils.metricas_projeto import calcular_metricas_projeto

class AnalisadorDesempenho:
    """
    Sistema de análise de desempenho baseado em Earned Value Management
    Base: PMBOK Guide, NASA EVM Handbook, ANSI/EIA-748
    """
    
    def __init__(self):
        pass
    
    def calcular_spi(self, projeto):
        """
        Calcular Schedule Performance Index (SPI)
        SPI = Earned Value (EV) / Planned Value (PV)
        """
        metricas = calcular_metricas_projeto(projeto.id)
        if not metricas or metricas['total_tarefas'] == 0:
            return 1.0
        
        return metricas['spi']
    
    def analisar_situacao_projeto(self, projeto):
        """
        Analisar a situação atual do projeto baseado em métricas EVM
        """
        metricas = calcular_metricas_projeto(projeto.id)
        if not metricas:
            return {'erro': 'Não foi possível calcular métricas'}
            
        spi = metricas['spi']
        porcentagem_atraso = (1 - spi) * 100
        
        # Determinar status baseado no SPI
        if spi >= 1.1:
            status = "ADIANTADO"
            cor = "verde"
            explicacao = f"Projeto {abs(porcentagem_atraso):.1f}% adiantado"
        elif spi >= 0.9:
            status = "NO PRAZO" 
            cor = "amarelo"
            explicacao = "Projeto dentro do cronograma"
        elif spi >= 0.7:
            status = "ATRASO MODERADO"
            cor = "laranja"
            explicacao = f"Projeto {porcentagem_atraso:.1f}% atrasado"
        else:
            status = "ATRASO CRÍTICO"
            cor = "vermelho"
            explicacao = f"Projeto {porcentagem_atraso:.1f}% atrasado"
        
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
            'taxa_conclusao': metricas['taxa_conclusao']
        }