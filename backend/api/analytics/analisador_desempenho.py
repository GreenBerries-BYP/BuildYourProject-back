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
                'tarefas_pendentes': 0,
                'taxa_conclusao': 100,
                'probabilidade_atraso': 0,
                'projeto_concluido': True,
                'dias_atraso': 0,
                'spi_calculado': 1.0
            }
        
        spi = metricas['spi']
        dias_restantes_reais = metricas['dias_restantes']
        tarefas_pendentes = metricas['total_tarefas'] - metricas['tarefas_concluidas']
        
        # GERAR EXPLICAÇÃO BASEADA NA SITUAÇÃO
        explicacao = self._gerar_explicacao_situacao(
            spi, dias_atraso, dias_restantes_reais, tarefas_pendentes
        )
        
        # DETERMINAR STATUS BASEADO NO SPI
        if spi >= 1.1:
            status = "ADIANTADO"
            cor = "verde"
        elif spi >= 0.95:
            status = "NO PRAZO" 
            cor = "verde-claro"
        elif spi >= 0.9:
            status = "ATENÇÃO" 
            cor = "amarelo"
        elif spi >= 0.7:
            status = "ATRASO MODERADO"
            cor = "laranja"
        else:
            status = "ATRASO CRÍTICO"
            cor = "vermelho"
        
        return {
            'status': status,
            'cor': cor,
            'explicacao': explicacao,
            'dias_restantes': dias_restantes_reais,
            'tarefas_atrasadas': metricas['tarefas_atrasadas'],
            'tarefas_pendentes': tarefas_pendentes,
            'taxa_conclusao': metricas['taxa_conclusao'],
            'probabilidade_atraso': 0,  # Será calculado depois
            'projeto_concluido': False,
            'dias_atraso': dias_atraso,
            'spi_calculado': spi
        }
    
    def _gerar_explicacao_situacao(self, spi, dias_atraso, dias_restantes, tarefas_pendentes):
        """Gera explicação contextual baseada na situação do projeto"""
        
        # SE HOUVER ATRASO
        if dias_atraso > 0:
            return f"Projeto com {dias_atraso} dias de atraso. Restam {dias_restantes} dias para concluir {tarefas_pendentes} tarefas"
        
        # SE NÃO HOUVER ATRASO
        if dias_restantes > 0:
            return f"{dias_restantes} dias restantes para concluir {tarefas_pendentes} tarefas"
        else:
            return f"Prazo finalizado. {tarefas_pendentes} tarefas pendentes"
    
    def _gerar_mensagem_conclusao(self, dias_antecedencia):
        """Gera mensagem personalizada para projeto concluído"""
        if dias_antecedencia > 0:
            return f"Parabéns! Projeto concluído com {dias_antecedencia} dias de antecedência"
        elif dias_antecedencia == 0:
            return "Parabéns! Projeto concluído exatamente no prazo"
        else:
            dias_atraso = abs(dias_antecedencia)
            return f"Projeto concluído com {dias_atraso} dias de atraso"
