# analisador_desempenho.py - ATUALIZADO

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
        
        # Calcular dias de atraso baseado no VAC
        dias_atraso = max(0, -metricas['vac'])
        
        # PROJETO CONCLUÍDO
        if metricas['taxa_conclusao'] == 100:
            dias_antecedencia = max(0, (projeto.end_date - timezone.now()).days)
            mensagem_conclusao = self._gerar_mensagem_conclusao(dias_antecedencia)
            
            return {
                'status': "PROJETO CONCLUÍDO",
                'cor': "verde",
                'explicacao': mensagem_conclusao,
                'dias_restantes': dias_antecedencia,  # Dias de antecedência
                'tarefas_atrasadas': 0,
                'taxa_conclusao': 100,
                'probabilidade_atraso': 0,
                'projeto_concluido': True,
                'dias_atraso': 0,
                'spi_calculado': 1.0
            }
        
        spi = metricas['spi']
        dias_restantes_reais = metricas['dias_restantes']
        
        # DETERMINAR STATUS BASEADO NO SPI
        if spi >= 1.1:
            status = "ADIANTADO"
            cor = "verde"
            if dias_atraso > 0:
                explicacao = f"Projeto adiantado, mas com {dias_atraso} dias de atraso acumulado"
            else:
                explicacao = "Projeto está adiantado em relação ao planejado"
        elif spi >= 0.95:
            status = "NO PRAZO" 
            cor = "verde-claro"
            if dias_atraso > 0:
                explicacao = f"Projeto no prazo, mas com {dias_atraso} dias de atraso acumulado"
            else:
                explicacao = "Projeto dentro do cronograma planejado"
        elif spi >= 0.9:
            status = "ATENÇÃO" 
            cor = "amarelo"
            if dias_atraso > 0:
                explicacao = f"Projeto com {dias_atraso} dias de atraso - requer atenção"
            else:
                explicacao = "Projeto próximo do limite - monitorar de perto"
        elif spi >= 0.7:
            status = "ATRASO MODERADO"
            cor = "laranja"
            explicacao = f"Projeto com {dias_atraso} dias de atraso - ação corretiva necessária"
        else:
            status = "ATRASO CRÍTICO"
            cor = "vermelho"
            explicacao = f"Projeto com {dias_atraso} dias de atraso - intervenção urgente necessária"
        
        return {
            'status': status,
            'cor': cor,
            'explicacao': explicacao,
            'dias_restantes': dias_restantes_reais,
            'tarefas_atrasadas': metricas['tarefas_atrasadas'],
            'taxa_conclusao': metricas['taxa_conclusao'],
            'probabilidade_atraso': 0,  # Será calculado depois
            'projeto_concluido': False,
            'dias_atraso': dias_atraso,
            'spi_calculado': spi
        }
    
    def _gerar_mensagem_conclusao(self, dias_antecedencia):
        """Gera mensagem personalizada para projeto concluído"""
        if dias_antecedencia > 0:
            return f"Parabéns! Projeto concluído com {dias_antecedencia} dias de antecedência"
        elif dias_antecedencia == 0:
            return "Parabéns! Projeto concluído exatamente no prazo"
        else:
            dias_atraso = abs(dias_antecedencia)
            return f"Projeto concluído com {dias_atraso} dias de atraso"
