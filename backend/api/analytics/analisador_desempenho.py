from django.utils import timezone
from ..utils.metricas_projeto import calcular_metricas_projeto

class AnalisadorDesempenho:
    """
    SISTEMA DE ANÁLISE DE DESEMPENHO BASEADO EM EARNED VALUE MANAGEMENT
    
    Referências: 
    - PMBOK Guide 7th Edition - Earned Value Management
    - NASA EVM Handbook
    - ANSI/EIA-748 Standard
    """
    
    def __init__(self):
        pass
    
    def calcular_spi(self, projeto):
        """
        Calcula Schedule Performance Index (SPI) conforme padrão EVM
        
        SPI = Earned Value (EV) / Planned Value (PV)
        """
        metricas = calcular_metricas_projeto(projeto.id)
        if not metricas or metricas['total_tarefas'] == 0:
            return 1.0
        
        return metricas['spi']
    
    def analisar_situacao_projeto(self, projeto):
        """
        Analisa a situação atual do projeto baseado em múltiplas métricas EVM
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