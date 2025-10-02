# sistema_sugestoes.py - ATUALIZADO PARA INTEGRAR COM FRONTEND

from ..utils.metricas_projeto import calcular_metricas_projeto
from ..models import UserProject, Task, TaskAssignee
from django.utils import timezone

class SistemaSugestoes:
    """
    SISTEMA DE SUGESTÕES INTELIGENTES BASEADO EM MÉTRICAS EVM
    
    Base: PMBOK Guide 7th Edition, NASA EVM Handbook, ANSI/EIA-748
    """
    
    @staticmethod
    def gerar_sugestoes(projeto):
        """
        Gera sugestões contextuais baseadas em análise EVM do projeto
        """
        sugestoes = []
        metricas = calcular_metricas_projeto(projeto.id)
        
        if not metricas:
            return sugestoes
        
        spi = metricas['spi']
        sv = metricas['sv']
        tcpi = metricas['tcpi']
        vac = metricas['vac']
        tarefas_atrasadas = metricas['tarefas_atrasadas']
        dias_restantes = metricas['dias_restantes']

        # projeto concluido, não retorna sugestão.
        if metricas['taxa_conclusao'] == 100:
            return []
        
        # 🔴 SUGESTÃO 1: PROJETO ATRASADO (SPI BAIXO)
        if spi < 0.9:
            sugestoes.append({
                'id': 'priorizar_atrasadas',
                'titulo': '🎯 Priorizar Tarefas Atrasadas',
                'descricao': f'SPI {spi:.2f} indica atraso. {tarefas_atrasadas} tarefas com prazo vencido',
                'acao': 'priorizar_atrasadas',
                'prioridade': 'alta' if spi < 0.7 else 'media'
            })
        
        # 🔴 SUGESTÃO 2: PERFORMANCE INSUSTENTÁVEL (TCPI ALTO)
        if tcpi > 1.2:
            sugestoes.append({
                'id': 'revisar_metas',
                'titulo': '📈 Revisar Metas do Projeto',
                'descricao': f'TCPI {tcpi:.2f} indica necessidade de performance muito acima do planejado',
                'acao': 'revisar_metas',
                'prioridade': 'alta'
            })
        
        # 🔴 SUGESTÃO 3: PREVISÃO DE ATRASO (VAC NEGATIVO)
        if vac < -7:
            sugestoes.append({
                'id': 'ajustar_prazos',
                'titulo': '⚠️ Ajustar Prazos Finais',
                'descricao': f'Previsão de {abs(vac):.0f} dias de atraso no término. Restam {dias_restantes} dias',
                'acao': 'ajustar_prazos', 
                'prioridade': 'alta' if vac < -14 else 'media'
            })
        
        # 🔴 SUGESTÃO 4: CARGA DESBALANCEADA
        carga_desequilibrada = SistemaSugestoes._verificar_carga_desequilibrada(projeto)
        if carga_desequilibrada['desequilibrio']:
            sugestoes.append({
                'id': 'balancear_carga',
                'titulo': '⚖️ Balancear Carga de Trabalho',
                'descricao': f"Diferença de {carga_desequilibrada['diferenca']} tarefas entre membros",
                'acao': 'balancear_carga',
                'prioridade': 'media'
            })
        
        # 🔴 SUGESTÃO 5: BAIXA TAXA DE CONCLUSÃO
        if metricas['taxa_conclusao'] < 30 and dias_restantes < 7:
            sugestoes.append({
                'id': 'acelerar_conclusao',
                'titulo': '🚀 Acelerar Conclusão',
                'descricao': f'Apenas {metricas["taxa_conclusao"]}% concluído com {dias_restantes} dias restantes',
                'acao': 'acelerar_conclusao',
                'prioridade': 'alta'
            })
        
        # 🔵 SUGESTÃO 6: PROJETO SAUDÁVEL
        if spi >= 1.0 and tcpi <= 1.1 and vac >= 0:
            sugestoes.append({
                'id': 'manter_ritmo',
                'titulo': '✅ Manter Ritmo Atual',
                'descricao': 'Projeto está no caminho certo! Continue com o bom trabalho',
                'acao': 'manter_ritmo',
                'prioridade': 'baixa'
            })
        
        return sorted(sugestoes, key=lambda x: {'alta': 3, 'media': 2, 'baixa': 1}[x['prioridade']], reverse=True)
    
    @staticmethod
    def _verificar_carga_desequilibrada(projeto):
        """Verifica desbalanceamento na carga de trabalho da equipe"""
        usuarios = UserProject.objects.filter(project=projeto)
        cargas = []
        
        for up in usuarios:
            tarefas_pendentes = Task.objects.filter(
                project_phase__project=projeto,
                is_completed=False,
                taskassignee__user=up.user
            ).count()
            cargas.append(tarefas_pendentes)
        
        if not cargas:
            return {'desequilibrio': False, 'diferenca': 0}
        
        diferenca = max(cargas) - min(cargas)
        return {
            'desequilibrio': diferenca > 3,
            'diferenca': diferenca,
            'maior_carga': max(cargas),
            'menor_carga': min(cargas)
        }