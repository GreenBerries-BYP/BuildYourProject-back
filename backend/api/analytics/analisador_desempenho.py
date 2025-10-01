from django.utils import timezone
from api.utils.metricas_projeto import calcular_metricas_projeto

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
            
        spi = metricas['spi']
        dias_restantes = metricas['dias_restantes']
        dias_decorridos = metricas['dias_decorridos']
        tarefas_concluidas = metricas['tarefas_concluidas']
        total_tarefas = metricas['total_tarefas']
        
        # LÓGICA CORRIGIDA: Projeto que termina HOJE sem nada feito = EMERGÊNCIA
        if dias_restantes == 0 and tarefas_concluidas == 0:
            status = "EMERGÊNCIA - PRAZO HOJE"
            cor = "vermelho"
            explicacao = "Projeto termina HOJE sem tarefas concluídas"
            probabilidade_atraso = 99
            
        elif dias_restantes == 0 and tarefas_concluidas < total_tarefas:
            status = "ATRASADO - PRAZO HOJE"
            cor = "vermelho" 
            explicacao = f"Projeto termina HOJE com {tarefas_concluidas}/{total_tarefas} tarefas"
            probabilidade_atraso = 95
            
        elif dias_restantes < 3 and tarefas_concluidas == 0:
            status = "CRÍTICO - PRAZO CURTO"
            cor = "vermelho"
            explicacao = f"Apenas {dias_restantes} dias restantes sem progresso"
            probabilidade_atraso = 90
            
        elif dias_decorridos == 0:
            # Projeto começou hoje - risco baixo
            status = "RECÉM-INICIADO"
            cor = "azul"
            explicacao = "Projeto iniciado hoje"
            probabilidade_atraso = 10
            
        elif tarefas_concluidas == 0 and dias_decorridos > 0:
            # Projeto começou mas não tem progresso - risco médio
            percentual_tempo_decorrido = (dias_decorridos / metricas['total_dias']) * 100
            
            if percentual_tempo_decorrido > 50:
                status = "GRAVE - SEM PROGRESSO"
                cor = "vermelho"
                explicacao = f"{percentual_tempo_decorrido:.0f}% do tempo passou sem progresso"
                probabilidade_atraso = 85
            elif percentual_tempo_decorrido > 25:
                status = "ALERTA - SEM PROGRESSO"
                cor = "laranja"
                explicacao = f"{percentual_tempo_decorrido:.0f}% do tempo passou sem progresso"
                probabilidade_atraso = 60
            else:
                status = "ATENÇÃO - SEM PROGRESSO"
                cor = "amarelo"
                explicacao = f"{dias_decorridos} dias sem tarefas concluídas"
                probabilidade_atraso = 40
                
        else:
            # Projeto com progresso normal - usar SPI
            porcentagem_atraso = (1 - spi) * 100
            
            if spi >= 1.1:
                status = "ADIANTADO"
                cor = "verde"
                explicacao = f"Projeto {abs(porcentagem_atraso):.1f}% adiantado"
                probabilidade_atraso = 5
            elif spi >= 0.9:
                status = "NO PRAZO" 
                cor = "amarelo"
                explicacao = "Projeto dentro do cronograma"
                probabilidade_atraso = 15
            elif spi >= 0.7:
                status = "ATRASO MODERADO"
                cor = "laranja"
                explicacao = f"Projeto {porcentagem_atraso:.1f}% atrasado"
                probabilidade_atraso = 40
            else:
                status = "ATRASO CRÍTICO"
                cor = "vermelho"
                explicacao = f"Projeto {porcentagem_atraso:.1f}% atrasado"
                probabilidade_atraso = 75
        
        return {
            'status': status,
            'cor': cor,
            'explicacao': explicacao,
            'probabilidade_atraso': probabilidade_atraso,
            'spi': round(spi, 3),
            'sv': metricas['sv'],
            'tcpi': metricas['tcpi'],
            'eac': metricas['eac'],
            'vac': metricas['vac'],
            'dias_restantes': dias_restantes,
            'tarefas_atrasadas': metricas['tarefas_atrasadas'],
            'taxa_conclusao': metricas['taxa_conclusao'],
            'dias_decorridos': dias_decorridos,
            'total_tarefas': total_tarefas,
            'tarefas_concluidas': tarefas_concluidas
        }
