from ..utils.metricas_projeto import calcular_metricas_projeto
from ..models import UserProject, Task, TaskAssignee

class SistemaSugestoes:
    """
    SISTEMA DE SUGESTÕES BASEADO EM ANÁLISE DE MÉTRICAS EVM
    
    Gera recomendações baseadas em:
    - Schedule Performance Index (SPI)
    - Schedule Variance (SV)
    - To Complete Performance Index (TCPI)
    - Variance at Completion (VAC)
    """
    
    @staticmethod
    def gerar_sugestoes(projeto):
        """
        Gera sugestões baseadas em análise de métricas EVM
        """
        sugestoes = []
        metricas = calcular_metricas_projeto(projeto.id)
        
        if not metricas:
            return sugestoes
        
        spi = metricas['spi']
        sv = metricas['sv']
        tcpi = metricas['tcpi']
        vac = metricas['vac']
        
        # SUGESTÃO 1: PROJETO ATRASADO (SPI BAIXO)
        if spi < 0.9:
            sugestoes.append({
                'id': 'priorizar_atrasadas',
                'titulo': '🎯 Priorizar Tarefas Atrasadas',
                'descricao': f'SPI {spi:.2f} indica atraso. Foque nas {metricas["tarefas_atrasadas"]} tarefas com prazo vencido',
                'acao': 'priorizar_atrasadas',
                'prioridade': 'alta'
            })
        
        # SUGESTÃO 2: PERFORMANCE INSUSTENTÁVEL (TCPI ALTO)
        if tcpi > 1.2:
            sugestoes.append({
                'id': 'revisar_metas',
                'titulo': '📈 Revisar Metas do Projeto',
                'descricao': f'TCPI {tcpi:.2f} indica necessidade de performance muito acima do planejado',
                'acao': 'revisar_metas',
                'prioridade': 'alta'
            })
        
        # SUGESTÃO 3: PREVISÃO DE ATRASO (VAC NEGATIVO)
        if vac < -7:
            sugestoes.append({
                'id': 'ajustar_prazos',
                'titulo': '⚠️ Ajustar Prazos Finais',
                'descricao': f'Previsão de {abs(vac):.0f} dias de atraso no término',
                'acao': 'ajustar_prazos', 
                'prioridade': 'media'
            })
        
        # SUGESTÃO 4: CARGA DESBALANCEADA
        if SistemaSugestoes._verificar_carga_desequilibrada(projeto):
            sugestoes.append({
                'id': 'balancear_carga',
                'titulo': '⚖️ Balancear Carga de Trabalho',
                'descricao': 'Distribuir tarefas de forma mais equilibrada entre a equipe',
                'acao': 'balancear_carga',
                'prioridade': 'media'
            })
        
        return sorted(sugestoes, key=lambda x: {'alta': 3, 'media': 2, 'baixa': 1}[x['prioridade']], reverse=True)
    
    @staticmethod
    def _verificar_carga_desequilibrada(projeto):
        """Verifica se há desbalanceamento na carga de trabalho"""
        usuarios = UserProject.objects.filter(project=projeto)
        cargas = []
        
        for up in usuarios:
            tarefas_pendentes = Task.objects.filter(
                project_phase__project=projeto,
                is_completed=False,
                taskassignee__user=up.user
            ).count()
            cargas.append(tarefas_pendentes)
        
        return cargas and (max(cargas) - min(cargas) > 3)